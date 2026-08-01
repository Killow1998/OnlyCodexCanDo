def assert-true [condition: bool, message: string] {
  if not $condition {
    error make {msg: $"ASSERTION FAILED: ($message)"}
  }
}

def assert-equal [actual: any, expected: any, message: string] {
  if $actual != $expected {
    error make {msg: $"ASSERTION FAILED: ($message); expected=($expected | to json --raw) actual=($actual | to json --raw)"}
  }
}

def save-json [file: path, value: any] {
  mkdir ($file | path dirname)
  $"($value | to json --indent 2)(char nl)" | save --raw --force $file
}

def fake-codex-source [] {
  r#'def save-json [file: path, value: any] {
  $"($value | to json --indent 2)(char nl)" | save --raw --force $file
}

def --wrapped main [...args: string] {
  let root = $env.CODEX_LFE_FAKE_ROOT
  let inventory_path = ($root | path join "inventory.json")
  let marketplaces_path = ($root | path join "marketplaces.json")
  if $args == ["plugin" "list" "--json"] {
    print (open --raw $inventory_path)
    return
  }
  if $args == ["plugin" "marketplace" "list" "--json"] {
    print (open --raw $marketplaces_path)
    return
  }
  if ($args | first 4) == ["plugin" "marketplace" "add" "https://github.com/Cjbuilds/Codex-Orchestration.git"] {
    let value = {
      marketplaces: [{
        name: "codex-orchestration"
        root: ($root | path join "orchestration-marketplace")
        marketplaceSource: {sourceType: "git", source: "https://github.com/Cjbuilds/Codex-Orchestration.git"}
      }]
    }
    save-json $marketplaces_path $value
    print '{"added":true}'
    return
  }
  if ($args | first 3) == ["plugin" "add" "codex-orchestration@codex-orchestration"] {
    let entry = {
      pluginId: "codex-orchestration@codex-orchestration"
      name: "codex-orchestration"
      marketplaceName: "codex-orchestration"
      version: "0.9.3"
      installed: true
      enabled: true
      source: {source: "local", path: ($root | path join "orchestration")}
      marketplaceSource: {sourceType: "git", source: "https://github.com/Cjbuilds/Codex-Orchestration.git"}
      installPolicy: "AVAILABLE"
      authPolicy: "ON_INSTALL"
    }
    save-json $inventory_path {installed: [$entry], available: []}
    print '{"installed":true}'
    return
  }
  print -e $"unexpected fake codex args: ($args | to json --raw)"
  exit 71
}
'#
}

def fake-configurer-source [] {
  r#'import json
import os
import sys
from pathlib import Path

root = Path(os.environ["CODEX_LFE_FAKE_ROOT"])
state_path = root / "routing.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
args = sys.argv[1:]

def save():
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

def arg_value(flag):
    if flag not in args:
        return None
    return args[args.index(flag) + 1]

def parse_route(seat, default=None):
    agent = arg_value(f"--{seat}-agent")
    if agent is not None:
        return {"kind": "agent", "agent": agent}
    model = arg_value(f"--{seat}-model")
    if model is not None:
        return {"kind": "model", "model": model, "effort": arg_value(f"--{seat}-effort")}
    if f"--{seat}-fable" in args:
        return {"kind": "fable", "effort": arg_value(f"--{seat}-effort")}
    if f"--{seat}-opus" in args:
        return {"kind": "opus", "effort": arg_value(f"--{seat}-effort")}
    return default or {"kind": "none"}

def summary(route, absent):
    if not route or route.get("kind") == "none":
        return absent
    if route["kind"] == "agent":
        return "custom agent " + route["agent"]
    if route["kind"] == "fable":
        return "Claude Fable 5 " + route["effort"]
    if route["kind"] == "opus":
        return "Claude Opus 5 " + route["effort"]
    return route["model"] + "@" + route["effort"]

if "--status" in args:
    if not state.get("installed", False):
        print("Native policy: not installed")
        if "--require-effective" in args:
            sys.exit(1)
        sys.exit(0)
    print("Native policy: installed and effective in fake workspace")
    print("Executor: " + summary(state["executor"], "none"))
    print("Planner: " + summary(state.get("planner"), "root"))
    print("Advisor: " + summary(state.get("advisor"), "none"))
    print("Designer: " + summary(state.get("designer"), "none"))
    sys.exit(0)

if state.get("fail_apply", False) and "--apply" in args:
    print("simulated apply failure", file=sys.stderr)
    sys.exit(72)

if "--disable" in args:
    print("NATIVE_DISABLE_PREVIEW")
    if "--apply" in args:
        state["installed"] = False
        save()
    sys.exit(0)

print("NATIVE_SETUP_PREVIEW")
if "--apply" in args:
    state["installed"] = True
    state["executor"] = parse_route("executor")
    state["planner"] = parse_route("planner")
    state["advisor"] = parse_route("advisor")
    state["designer"] = parse_route("designer")
    save()
'#
}

def base-luna [version: string] {
  {
    slug: "gpt-5.6-luna"
    default_reasoning_level: "medium"
    supported_reasoning_levels: [
      {effort: "low", description: "low"}
      {effort: "medium", description: "medium"}
      {effort: "high", description: "high"}
      {effort: "xhigh", description: "xhigh"}
      {effort: "max", description: "max"}
    ]
    multi_agent_version: $version
    service_tiers: [{id: "priority", name: "Fast", description: "fast"}]
  }
}

def create-case [suite_root: path, name: string, options: record] {
  let root = ($suite_root | path join $name)
  let home = ($root | path join "home")
  let workspace = ($root | path join "workspace")
  let orchestration = ($root | path join "orchestration")
  let configurer = ($orchestration | path join "skills" "codex-orchestration" "scripts" "configure_native_routing.py")
  mkdir $home
  mkdir $workspace
  mkdir ($configurer | path dirname)
  fake-configurer-source | save --raw $configurer
  let fake_codex = ($root | path join "fake-codex.nu")
  fake-codex-source | save --raw $fake_codex

  let version = ($options | get -o version | default "v1")
  mut models = [{slug: "gpt-5.6-sol", multi_agent_version: "v2"} (base-luna $version)]
  let catalog_variant = ($options | get -o catalog_variant | default "normal")
  if $catalog_variant == "missing" {
    $models = [$models.0]
  } else if $catalog_variant == "duplicate" {
    $models = ($models | append (base-luna $version))
  } else if $catalog_variant == "no-max" {
    let luna = (base-luna $version | upsert supported_reasoning_levels [{effort: "low"} {effort: "high"}])
    $models = [$models.0 $luna]
  } else if $catalog_variant == "no-fast" {
    let luna = (base-luna $version | upsert service_tiers [{id: "standard", name: "Standard"}])
    $models = [$models.0 $luna]
  }
  save-json ($home | path join "models_cache.json") {models: $models, unrelated: {preserve: true}}

  let config_text = ($options | get -o config_text | default "# preserved\n[unrelated]\nvalue = 7\n")
  $config_text | save --raw ($home | path join "config.toml")

  let installed = ($options | get -o installed | default true)
  let canonical = ($options | get -o canonical | default true)
  let source_url = if $canonical { "https://github.com/Cjbuilds/Codex-Orchestration.git" } else { "https://example.invalid/not-canonical.git" }
  let entry = {
    pluginId: "codex-orchestration@codex-orchestration"
    name: "codex-orchestration"
    marketplaceName: "codex-orchestration"
    version: "0.9.3"
    installed: true
    enabled: true
    source: {source: "local", path: $orchestration}
    marketplaceSource: {sourceType: "git", source: $source_url}
    installPolicy: "AVAILABLE"
    authPolicy: "ON_INSTALL"
  }
  save-json ($root | path join "inventory.json") {
    installed: (if $installed { [$entry] } else { [] })
    available: []
  }
  save-json ($root | path join "marketplaces.json") {
    marketplaces: (if $installed {
      [{name: "codex-orchestration", root: ($root | path join "market"), marketplaceSource: {sourceType: "git", source: $source_url}}]
    } else { [] })
  }
  save-json ($root | path join "routing.json") {
    installed: ($options | get -o routing_installed | default true)
    executor: {kind: "model", model: "gpt-5.6-luna", effort: "max"}
    planner: {kind: "none"}
    advisor: {kind: "model", model: "gpt-5.6-terra", effort: "max"}
    designer: {kind: "none"}
    fail_apply: ($options | get -o fail_apply | default false)
  }
  if ($options | get -o agent_conflict | default false) {
    mkdir ($home | path join "agents")
    'name = "codex_lfe_executor"\nmodel = "not-luna"\n' | save --raw ($home | path join "agents" "codex_lfe_executor.toml")
  }
  {root: $root, home: $home, workspace: $workspace, fake_codex: $fake_codex}
}

def run-lfs [script: path, case: record, command: string] {
  with-env {CODEX_LFE_FAKE_ROOT: ($case.root | into string)} {
    do {
      ^nu $script $command --codex-home $case.home --codex-bin $case.fake_codex --python-bin python --workspace $case.workspace
    } | complete
  }
}

def file-hash [file: path] {
  open --raw $file | hash sha256
}

def main [] {
  let script = ($env.FILE_PWD | path join "codex-lfe.nu")
  let temp_root = if ("TMPDIR" in $env) {
    $env.TMPDIR
  } else if ("TEMP" in $env) {
    $env.TEMP
  } else if ("TMP" in $env) {
    $env.TMP
  } else {
    error make {msg: "No operating-system temporary directory is available"}
  }
  let suite_root = ($temp_root | path join $"codex-lfe-tests-(random uuid)")
  mkdir $suite_root
  mut passed = 0

  print "1. fresh setup installs canonical dependency"
  let fresh = (create-case $suite_root "fresh" {installed: false, routing_installed: false})
  let fresh_result = (run-lfs $script $fresh "setup")
  assert-equal $fresh_result.exit_code 0 "fresh setup should succeed"
  assert-true ($fresh_result.stdout | str contains "RESTART_REQUIRED") "fresh setup must require restart"
  let fresh_state = (open ($fresh.home | path join ".codex-lfe" "state.json"))
  assert-equal $fresh_state.routing_setup_status "complete" "fresh state should be complete"
  assert-equal $fresh_state.orchestration_installed_by_tool true "fresh setup should record dependency install"
  let fresh_inventory = (open ($fresh.root | path join "inventory.json"))
  assert-equal $fresh_inventory.installed.0.marketplaceSource.source "https://github.com/Cjbuilds/Codex-Orchestration.git" "dependency source should be canonical"
  $passed += 1

  print "2. already-installed canonical Orchestration is preserved"
  let installed = (create-case $suite_root "installed" {})
  let installed_result = (run-lfs $script $installed "setup")
  assert-equal $installed_result.exit_code 0 "installed dependency setup should succeed"
  let installed_state = (open ($installed.home | path join ".codex-lfe" "state.json"))
  assert-equal $installed_state.orchestration_installed_by_tool false "existing dependency should not be claimed"
  let installed_routing = (open ($installed.root | path join "routing.json"))
  assert-equal $installed_routing.advisor.model "gpt-5.6-terra" "Advisor should be preserved"
  assert-equal $installed_routing.executor.agent "codex_lfe_executor" "Executor should use the custom agent"
  $passed += 1

  print "3. wrong-source Orchestration is rejected"
  let wrong = (create-case $suite_root "wrong-source" {canonical: false})
  let wrong_config_hash = (file-hash ($wrong.home | path join "config.toml"))
  let wrong_result = (run-lfs $script $wrong "setup")
  assert-true ($wrong_result.exit_code != 0) "wrong source should fail"
  assert-equal (file-hash ($wrong.home | path join "config.toml")) $wrong_config_hash "wrong source should not write config"
  assert-true (not (($wrong.home | path join ".codex-lfe" "state.json") | path exists)) "wrong source should not create state"
  $passed += 1

  print "4. Luna v1 creates a local semantic shim"
  let shim = ($installed.home | path join "model-catalogs" "codex-lfe-luna-v2.json")
  assert-true ($shim | path exists) "v1 setup should create shim"
  let shim_models = (open $shim | get models)
  assert-equal ($shim_models | where slug == "gpt-5.6-luna" | first | get multi_agent_version) "v2" "shim should change Luna to v2"
  assert-equal ($shim_models | where slug == "gpt-5.6-sol" | first | get multi_agent_version) "v2" "shim should preserve other models"
  $passed += 1

  print "5. Luna v2 is a catalog/config no-op"
  let v2 = (create-case $suite_root "v2" {version: "v2"})
  let v2_before = (open --raw ($v2.home | path join "config.toml"))
  let v2_result = (run-lfs $script $v2 "setup")
  assert-equal $v2_result.exit_code 0 "v2 setup should succeed"
  assert-equal (open --raw ($v2.home | path join "config.toml")) $v2_before "v2 setup should preserve config bytes"
  assert-true (not (($v2.home | path join "model-catalogs" "codex-lfe-luna-v2.json") | path exists)) "v2 setup should not create shim"
  $passed += 1

  print "6. invalid Luna catalog variants fail closed"
  for variant in ["missing" "duplicate" "no-max" "no-fast"] {
    let invalid = (create-case $suite_root $"invalid-($variant)" {catalog_variant: $variant})
    let before = (file-hash ($invalid.home | path join "config.toml"))
    let result = (run-lfs $script $invalid "setup")
    assert-true ($result.exit_code != 0) $"($variant) should fail"
    assert-equal (file-hash ($invalid.home | path join "config.toml")) $before $"($variant) should not change config"
    assert-true (not (($invalid.home | path join ".codex-lfe" "state.json") | path exists)) $"($variant) should not create state"
  }
  $passed += 1

  print "7. conflicting model_catalog_json produces zero writes"
  let conflict_config = (create-case $suite_root "config-conflict" {config_text: "model_catalog_json = \"C:\\\\other\\\\catalog.json\"\n[unrelated]\nvalue = 7\n"})
  let conflict_before = (open --raw ($conflict_config.home | path join "config.toml"))
  let conflict_result = (run-lfs $script $conflict_config "setup")
  assert-true ($conflict_result.exit_code != 0) "config conflict should fail"
  assert-equal (open --raw ($conflict_config.home | path join "config.toml")) $conflict_before "config conflict should preserve bytes"
  assert-true (not (($conflict_config.home | path join "agents" "codex_lfe_executor.toml") | path exists)) "config conflict should not create agent"
  $passed += 1

  print "8. conflicting custom agent is never overwritten"
  let conflict_agent = (create-case $suite_root "agent-conflict" {agent_conflict: true})
  let agent_path = ($conflict_agent.home | path join "agents" "codex_lfe_executor.toml")
  let agent_before = (open --raw $agent_path)
  let agent_result = (run-lfs $script $conflict_agent "setup")
  assert-true ($agent_result.exit_code != 0) "agent conflict should fail"
  assert-equal (open --raw $agent_path) $agent_before "agent conflict should preserve bytes"
  assert-true (not (($conflict_agent.home | path join ".codex-lfe" "state.json") | path exists)) "agent conflict should not create state"
  $passed += 1

  print "9. repeated setup is byte-idempotent"
  let idempotent_paths = [
    ($installed.home | path join "config.toml")
    ($installed.home | path join "agents" "codex_lfe_executor.toml")
    ($installed.home | path join "model-catalogs" "codex-lfe-luna-v2.json")
    ($installed.home | path join ".codex-lfe" "state.json")
    ($installed.root | path join "routing.json")
  ]
  let before_hashes = ($idempotent_paths | each {|path| file-hash $path})
  let idempotent_result = (run-lfs $script $installed "setup")
  assert-equal $idempotent_result.exit_code 0 "repeated setup should succeed"
  assert-true ($idempotent_result.stdout | str contains "ALREADY_CONFIGURED") "repeated setup should report idempotence"
  assert-equal ($idempotent_paths | each {|path| file-hash $path}) $before_hashes "repeated setup should change no bytes"
  $passed += 1

  print "10. mid-apply failure never claims success"
  let failing = (create-case $suite_root "mid-failure" {fail_apply: true})
  let failing_result = (run-lfs $script $failing "setup")
  assert-true ($failing_result.exit_code != 0) "simulated apply should fail"
  assert-true (not ($failing_result.stdout | str contains "RESTART_REQUIRED")) "failed setup must not require restart as success"
  let failing_state = (open ($failing.home | path join ".codex-lfe" "state.json"))
  assert-equal $failing_state.routing_setup_status "failed" "failed setup state must not be complete"
  $passed += 1

  print "11. disable restores exact bytes and prior routing"
  let disable_case = (create-case $suite_root "disable" {})
  let disable_config_before = (open --raw ($disable_case.home | path join "config.toml"))
  let setup_disable = (run-lfs $script $disable_case "setup")
  assert-equal $setup_disable.exit_code 0 "disable fixture setup should succeed"
  let disable_result = (run-lfs $script $disable_case "disable")
  assert-equal $disable_result.exit_code 0 "disable should succeed"
  assert-equal (open --raw ($disable_case.home | path join "config.toml")) $disable_config_before "disable should restore exact config bytes"
  assert-true (not (($disable_case.home | path join "agents" "codex_lfe_executor.toml") | path exists)) "disable should remove created agent"
  assert-true (not (($disable_case.home | path join ".codex-lfe" "state.json") | path exists)) "disable should remove state"
  let restored_routing = (open ($disable_case.root | path join "routing.json"))
  assert-equal $restored_routing.executor.model "gpt-5.6-luna" "disable should restore prior Executor"
  assert-equal $restored_routing.advisor.model "gpt-5.6-terra" "disable should restore prior Advisor"
  $passed += 1

  print "12. disable refuses managed drift"
  let drift = (create-case $suite_root "drift" {})
  let drift_setup = (run-lfs $script $drift "setup")
  assert-equal $drift_setup.exit_code 0 "drift fixture setup should succeed"
  let drift_agent = ($drift.home | path join "agents" "codex_lfe_executor.toml")
  (open --raw $drift_agent) + "# drift\n" | save --raw --force $drift_agent
  let drift_result = (run-lfs $script $drift "disable")
  assert-true ($drift_result.exit_code != 0) "disable should reject drift"
  assert-true (($drift.home | path join ".codex-lfe" "state.json") | path exists) "drift refusal should retain state"
  assert-equal (open ($drift.root | path join "routing.json") | get executor.agent) "codex_lfe_executor" "drift refusal should not alter routing"
  $passed += 1

  print "13. verify is static preflight, not a fake runtime confirmation"
  let verify_result = (run-lfs $script $installed "verify")
  assert-equal $verify_result.exit_code 0 "verify preflight should succeed"
  assert-true ($verify_result.stdout | str contains "READY_FOR_SPAWN") "verify should request a real spawn"
  assert-true (not ($verify_result.stdout | str contains "used and confirmed")) "verify must not fake runtime confirmation"
  $passed += 1

  let safe_root = ($suite_root | path expand | str replace --all "\\" "/")
  let safe_temp = ($temp_root | path expand | str replace --all "\\" "/")
  assert-true ($safe_root | str starts-with $"($safe_temp)/codex-lfe-tests-") "test cleanup target must remain in the temp directory"
  rm -r $suite_root
  print $"PASS: ($passed) CodexLFE regression groups"
}
