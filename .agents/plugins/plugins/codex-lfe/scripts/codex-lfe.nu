const PLUGIN_ID = "codex-orchestration@codex-orchestration"
const PLUGIN_NAME = "codex-orchestration"
const CANONICAL_SOURCE = "https://github.com/Cjbuilds/Codex-Orchestration.git"
const AGENT_NAME = "codex_lfe_executor"
const STATE_SCHEMA = 1

def fail [message: string] {
  error make {msg: $message}
}

def now [] {
  date now | format date "%+"
}

def normalized [value: path] {
  $value | path expand | str replace --all "\\" "/" | str lowercase
}

def is-listlike [value: any] {
  let kind = ($value | describe)
  ($kind | str starts-with "list") or ($kind | str starts-with "table")
}

def assert-managed-path [codex_home: path, target: path] {
  let home = (normalized $codex_home)
  let candidate = (normalized $target)
  if not ($candidate | str starts-with $"($home)/") {
    fail $"unsafe managed path outside CODEX_HOME: ($target)"
  }
}

def sha-text [content: string] {
  $content | hash sha256
}

def sha-file [file: path] {
  open --raw $file | hash sha256
}

def atomic-save [file: path, content: string] {
  let parent = ($file | path dirname)
  mkdir $parent
  let temporary = ($parent | path join $".codex-lfe-tmp-(random uuid)")
  $content | save --raw $temporary
  mv --force $temporary $file
}

def run-program [program: string, args: list<string>] {
  if ($program | str ends-with ".nu") {
    do { ^nu $program ...$args } | complete
  } else {
    do { ^$program ...$args } | complete
  }
}

def run-codex [codex_bin: string, args: list<string>] {
  run-program $codex_bin $args
}

def require-command [result: record, phase: string] {
  if $result.exit_code != 0 {
    fail $"($phase) failed with exit code ($result.exit_code)"
  }
  $result
}

def parse-json-output [result: record, phase: string] {
  require-command $result $phase | ignore
  try {
    $result.stdout | from json
  } catch {
    fail $"($phase) returned invalid JSON"
  }
}

def resolve-codex-home [requested: any] {
  if $requested != null {
    $requested | path expand
  } else if ("CODEX_HOME" in $env) {
    $env.CODEX_HOME | path expand
  } else if ("USERPROFILE" in $env) {
    $env.USERPROFILE | path join ".codex" | path expand
  } else if ("HOME" in $env) {
    $env.HOME | path join ".codex" | path expand
  } else {
    fail "could not resolve CODEX_HOME from CODEX_HOME, USERPROFILE, or HOME"
  }
}

def agent-content [] {
  [
    'name = "codex_lfe_executor"'
    'description = "Bounded Luna Max Fast executor managed by CodexLFE."'
    'model = "gpt-5.6-luna"'
    'model_reasoning_effort = "max"'
    'service_tier = "fast"'
    'developer_instructions = "Execute only the bounded packet from the root. Do not redesign the plan, contact planning roles, create descendants, or modify files outside assigned ownership. Preserve unrelated work, verify the slice, and report blockers instead of guessing."'
    ''
  ] | str join (char nl)
}

def inspect-catalog [catalog_path: path] {
  if not ($catalog_path | path exists) {
    fail $"model catalog does not exist: ($catalog_path)"
  }
  let raw = (open --raw $catalog_path)
  let parsed = try {
    $raw | from json
  } catch {
    fail "models_cache.json is not valid JSON"
  }
  let models = ($parsed | get -o models)
  if $models == null or not (is-listlike $models) {
    fail "models_cache.json must contain a models array"
  }
  let luna_matches = ($models | where {|model| ($model | get -o slug) == "gpt-5.6-luna"})
  if ($luna_matches | length) != 1 {
    fail "models_cache.json must contain exactly one gpt-5.6-luna record"
  }
  let luna = ($luna_matches | first)
  let effort_entries = ($luna | get -o supported_reasoning_levels)
  if $effort_entries == null or not (is-listlike $effort_entries) {
    fail "gpt-5.6-luna has no supported_reasoning_levels array"
  }
  let efforts = ($effort_entries | each {|entry|
    if (($entry | describe) | str starts-with "record") {
      $entry | get -o effort
    } else {
      $entry
    }
  })
  if not ($efforts | any {|effort| $effort == "max"}) {
    fail "gpt-5.6-luna does not support max reasoning"
  }
  let tiers = ($luna | get -o service_tiers)
  if $tiers == null or not (is-listlike $tiers) {
    fail "gpt-5.6-luna has no service_tiers array"
  }
  let fast_tiers = ($tiers | where {|tier|
    (($tier | get -o name | default "" | str lowercase) == "fast") and (($tier | get -o id) == "priority")
  })
  if ($fast_tiers | length) == 0 {
    fail "gpt-5.6-luna must expose Fast with service tier id priority"
  }
  let version = ($luna | get -o multi_agent_version)
  if $version not-in ["v1" "v2"] {
    fail $"unsupported gpt-5.6-luna multi_agent_version: ($version)"
  }
  {
    raw: $raw
    parsed: $parsed
    source_hash: (sha-text $raw)
    multi_agent_version: $version
  }
}

def shim-content [catalog: record] {
  let models = ($catalog.parsed.models | each {|model|
    if ($model | get -o slug) == "gpt-5.6-luna" {
      $model | upsert multi_agent_version "v2"
    } else {
      $model
    }
  })
  let updated = ($catalog.parsed | upsert models $models)
  $"($updated | to json --indent 2)(char nl)"
}

def config-info [raw: string] {
  let newline = if ($raw | str contains "\r\n") { "\r\n" } else { (char nl) }
  let rows = ($raw | split row $newline)
  mut in_table = false
  mut matches = []
  for row in ($rows | enumerate) {
    let trimmed = ($row.item | str trim)
    if ($trimmed | str starts-with "[") {
      $in_table = true
    }
    if (not $in_table) and ($row.item =~ '^\s*model_catalog_json\s*=') {
      $matches = ($matches | append $row)
    }
  }
  if ($matches | length) > 1 {
    fail "config.toml contains duplicate top-level model_catalog_json keys"
  }
  if ($matches | length) == 0 {
    return {newline: $newline, line: null, line_index: null, value: null}
  }
  let match = ($matches | first)
  let value = try {
    $match.item | from toml | get model_catalog_json
  } catch {
    fail "could not parse the top-level model_catalog_json line"
  }
  if not (($value | describe) | str starts-with "string") {
    fail "model_catalog_json must be a string"
  }
  {newline: $newline, line: $match.item, line_index: $match.index, value: $value}
}

def managed-catalog-line [catalog_path: path] {
  {model_catalog_json: ($catalog_path | path expand)} | to toml | str trim
}

def set-catalog-line [raw: string, info: record, line: string] {
  if $info.line_index == null {
    if ($raw | is-empty) {
      $"($line)($info.newline)"
    } else {
      $"($line)($info.newline)($raw)"
    }
  } else {
    $raw
    | split row $info.newline
    | enumerate
    | each {|row| if $row.index == $info.line_index { $line } else { $row.item }}
    | str join $info.newline
  }
}

def restore-catalog-line [raw: string, state: record] {
  let info = (config-info $raw)
  if $info.line != $state.managed_catalog_line {
    fail "config.toml model_catalog_json drifted; refusing disable"
  }
  let rows = ($raw | split row $info.newline)
  if $state.original_catalog_line == null {
    $rows
    | enumerate
    | where {|row| $row.index != $info.line_index}
    | get item
    | str join $info.newline
  } else {
    $rows
    | enumerate
    | each {|row| if $row.index == $info.line_index { $state.original_catalog_line } else { $row.item }}
    | str join $info.newline
  }
}

def dependency-status [codex_bin: string] {
  let inventory_result = (run-codex $codex_bin ["plugin" "list" "--json"])
  let inventory = (parse-json-output $inventory_result "codex plugin list")
  let installed = ($inventory | get -o installed | default [])
  let same_name = ($installed | where {|entry|
    (($entry | get -o name) == $PLUGIN_NAME) or (($entry | get -o pluginId) == $PLUGIN_ID)
  })
  if ($same_name | length) > 1 {
    fail "multiple Codex Orchestration plugin entries were found"
  }
  if ($same_name | length) == 0 {
    return {installed: false, entry: null, script: null}
  }
  let entry = ($same_name | first)
  if ($entry | get -o pluginId) != $PLUGIN_ID {
    fail "a same-name Codex Orchestration plugin has an unexpected plugin ID"
  }
  if ($entry | get -o enabled) != true {
    fail "canonical Codex Orchestration is installed but disabled"
  }
  let source = ($entry | get -o marketplaceSource)
  if $source == null or ($source | get -o sourceType) != "git" or ($source | get -o source) != $CANONICAL_SOURCE {
    fail "Codex Orchestration has a noncanonical marketplace source"
  }
  let plugin_path = ($entry | get -o source | get -o path)
  if $plugin_path == null {
    fail "canonical Codex Orchestration has no installed source path"
  }
  let script = ($plugin_path | path join "skills" "codex-orchestration" "scripts" "configure_native_routing.py")
  if not ($script | path exists) {
    fail "canonical configure_native_routing.py was not found in the installed plugin"
  }
  {installed: true, entry: $entry, script: ($script | path expand)}
}

def install-dependency [codex_bin: string] {
  let marketplace_result = (run-codex $codex_bin ["plugin" "marketplace" "list" "--json"])
  let marketplaces_json = (parse-json-output $marketplace_result "codex plugin marketplace list")
  let marketplaces = ($marketplaces_json | get -o marketplaces | default [])
  let named = ($marketplaces | where {|entry| ($entry | get -o name) == $PLUGIN_NAME})
  if ($named | length) > 1 {
    fail "multiple codex-orchestration marketplaces were found"
  }
  mut marketplace_added = false
  if ($named | length) == 1 {
    let source = ($named | first | get -o marketplaceSource)
    if $source == null or ($source | get -o sourceType) != "git" or ($source | get -o source) != $CANONICAL_SOURCE {
      fail "the codex-orchestration marketplace name points to a noncanonical source"
    }
  } else {
    print $"PREVIEW: add canonical marketplace ($CANONICAL_SOURCE)"
    require-command (run-codex $codex_bin ["plugin" "marketplace" "add" $CANONICAL_SOURCE "--json"]) "codex plugin marketplace add" | ignore
    $marketplace_added = true
  }
  print $"PREVIEW: install ($PLUGIN_ID)"
  require-command (run-codex $codex_bin ["plugin" "add" $PLUGIN_ID "--json"]) "codex plugin add" | ignore
  {marketplace_added: $marketplace_added}
}

def route-value [text: string, label: string] {
  let prefix = $"($label):"
  let lines = ($text | lines | where {|line| $line | str starts-with $prefix})
  if ($lines | length) != 1 {
    fail $"canonical routing status did not provide one ($label) line"
  }
  $lines | first | str replace $prefix "" | str trim
}

def parse-route [summary: string, seat: string] {
  if ($seat == "planner" and $summary == "root") or ($summary == "none") {
    return {kind: "none"}
  }
  if ($summary | str starts-with "custom agent ") {
    return {kind: "agent", agent: ($summary | str replace "custom agent " "")}
  }
  if ($summary | str starts-with "Claude Fable 5 ") {
    return {kind: "fable", effort: ($summary | str replace "Claude Fable 5 " "")}
  }
  if ($summary | str starts-with "Claude Opus 5 ") {
    return {kind: "opus", effort: ($summary | str replace "Claude Opus 5 " "")}
  }
  if $summary =~ '@[^@]+$' {
    let pieces = ($summary | split row "@")
    return {
      kind: "model"
      model: ($pieces | drop 1 | str join "@")
      effort: ($pieces | last)
    }
  }
  fail $"unsupported ($seat) route in canonical status: ($summary)"
}

def native-status [python_bin: string, script: path, codex_bin: string, codex_home: path, require_effective: bool] {
  mut args = [($script | into string) "--codex-bin" $codex_bin "--codex-home" ($codex_home | into string) "--status"]
  if $require_effective {
    $args = ($args | append "--require-effective")
  }
  let result = (run-program $python_bin $args)
  if $result.exit_code != 0 {
    fail $"canonical routing status failed with exit code ($result.exit_code)"
  }
  let installed = ($result.stdout | str contains "Native policy: installed")
  if not $installed {
    return {installed: false, executor: null, planner: {kind: "none"}, advisor: {kind: "none"}, designer: {kind: "none"}, raw: $result.stdout}
  }
  {
    installed: true
    executor: (parse-route (route-value $result.stdout "Executor") "executor")
    planner: (parse-route (route-value $result.stdout "Planner") "planner")
    advisor: (parse-route (route-value $result.stdout "Advisor") "advisor")
    designer: (parse-route (route-value $result.stdout "Designer") "designer")
    raw: $result.stdout
  }
}

def append-route-args [args: list<string>, seat: string, route: record] {
  if $route.kind == "none" {
    return $args
  }
  if $route.kind == "agent" {
    return ($args | append [$"--($seat)-agent" $route.agent])
  }
  if $route.kind == "model" {
    return ($args | append [$"--($seat)-model" $route.model $"--($seat)-effort" $route.effort])
  }
  if $route.kind == "fable" {
    return ($args | append [$"--($seat)-fable" $"--($seat)-effort" $route.effort])
  }
  if $route.kind == "opus" {
    return ($args | append [$"--($seat)-opus" $"--($seat)-effort" $route.effort])
  }
  fail $"unsupported saved route kind for ($seat): ($route.kind)"
}

def setup-args [script: path, codex_bin: string, codex_home: path, executor: record, planner: record, advisor: record, designer: record] {
  mut args = [($script | into string) "--codex-bin" $codex_bin "--codex-home" ($codex_home | into string)]
  $args = (append-route-args $args "executor" $executor)
  $args = (append-route-args $args "planner" $planner)
  $args = (append-route-args $args "advisor" $advisor)
  $args = (append-route-args $args "designer" $designer)
  $args
}

def state-paths [codex_home: path] {
  let state_dir = ($codex_home | path join ".codex-lfe")
  {
    state_dir: $state_dir
    state: ($state_dir | path join "state.json")
    restore: ($state_dir | path join "config-restore.json")
    config: ($codex_home | path join "config.toml")
    source_catalog: ($codex_home | path join "models_cache.json")
    generated_catalog: ($codex_home | path join "model-catalogs" "codex-lfe-luna-v2.json")
    agent: ($codex_home | path join "agents" "codex_lfe_executor.toml")
  }
}

def load-state [state_path: path, codex_home: path] {
  let state = try {
    open $state_path
  } catch {
    fail "CodexLFE state is unreadable; RECOVERY_REQUIRED"
  }
  if ($state | get -o schema_version) != $STATE_SCHEMA or ($state | get -o owner) != "CodexLFE" {
    fail "CodexLFE state has an unsupported schema or owner; RECOVERY_REQUIRED"
  }
  if (normalized ($state | get codex_home)) != (normalized $codex_home) {
    fail "CodexLFE state belongs to a different CODEX_HOME; RECOVERY_REQUIRED"
  }
  $state
}

def inspect-state [state: record] {
  mut issues = []
  if ($state | get -o routing_setup_status) != "complete" {
    $issues = ($issues | append $"routing_setup_status=($state | get -o routing_setup_status)")
  }
  let agent_path = ($state | get custom_agent_path)
  if not ($agent_path | path exists) {
    $issues = ($issues | append "custom agent is missing")
  } else if (sha-file $agent_path) != ($state | get custom_agent_hash) {
    $issues = ($issues | append "custom agent drift")
  }
  let generated = ($state | get -o generated_catalog_path)
  if $generated != null {
    if not ($generated | path exists) {
      $issues = ($issues | append "generated catalog is missing")
    } else if (sha-file $generated) != ($state | get generated_catalog_hash) {
      $issues = ($issues | append "generated catalog drift")
    }
  }
  let restore = ($state | get restore_snapshot_path)
  if not ($restore | path exists) {
    $issues = ($issues | append "restore snapshot is missing")
  } else if (sha-file $restore) != ($state | get restore_snapshot_hash) {
    $issues = ($issues | append "restore snapshot drift")
  }
  if ($state | get -o managed_catalog_line) != null {
    let config_path = ($state | get config_path)
    if not ($config_path | path exists) {
      $issues = ($issues | append "config.toml is missing")
    } else {
      let info = (config-info (open --raw $config_path))
      if $info.line != ($state | get managed_catalog_line) {
        $issues = ($issues | append "model_catalog_json drift")
      }
    }
  }
  $issues
}

def find-project-shadows [workspace: path, personal_agent: path] {
  mut current = ($workspace | path expand)
  mut shadows = []
  loop {
    let agents_dir = ($current | path join ".codex" "agents")
    if ($agents_dir | path exists) {
      for candidate in (glob ($agents_dir | path join "*.toml")) {
        if (normalized $candidate) != (normalized $personal_agent) {
          let content = (try { open --raw $candidate } catch { "" })
          if $content =~ '(?m)^\s*name\s*=\s*"codex_lfe_executor"\s*$' {
            $shadows = ($shadows | append ($candidate | path expand))
          }
        }
      }
    }
    let parent = ($current | path dirname)
    if (normalized $parent) == (normalized $current) {
      break
    }
    $current = $parent
  }
  $shadows
}

def command-status [codex_home: path, codex_bin: string, python_bin: string] {
  let paths = (state-paths $codex_home)
  let dependency = (dependency-status $codex_bin)
  if not ($paths.state | path exists) {
    print ({
      status: "NOT_CONFIGURED"
      codex_home: ($codex_home | into string)
      canonical_orchestration: (if $dependency.installed { "installed and enabled" } else { "missing" })
    } | to json --indent 2)
    return
  }
  let state = (load-state $paths.state $codex_home)
  let issues = (inspect-state $state)
  mut routing = "unavailable"
  if $dependency.installed {
    let native = (native-status $python_bin $dependency.script $codex_bin $codex_home false)
    $routing = if $native.installed { "installed" } else { "not installed" }
  }
  print ({
    status: (if ($issues | is-empty) { "CONFIGURED" } else { "RECOVERY_REQUIRED" })
    codex_home: ($codex_home | into string)
    canonical_orchestration: (if $dependency.installed { "installed and enabled" } else { "missing" })
    routing: $routing
    restart_required_from_setup: ($state | get -o restart_required | default false)
    issues: $issues
  } | to json --indent 2)
  if not ($issues | is-empty) {
    fail "CodexLFE managed state is unhealthy; RECOVERY_REQUIRED"
  }
}

def command-setup [codex_home: path, codex_bin: string, python_bin: string] {
  let paths = (state-paths $codex_home)
  for target in [$paths.state $paths.restore $paths.config $paths.generated_catalog $paths.agent] {
    assert-managed-path $codex_home $target
  }
  if ($paths.state | path exists) {
    let existing = (load-state $paths.state $codex_home)
    let issues = (inspect-state $existing)
    if not ($issues | is-empty) {
      fail $"CodexLFE already has unhealthy managed state: ($issues | str join ', '); RECOVERY_REQUIRED"
    }
    let dependency = (dependency-status $codex_bin)
    if not $dependency.installed {
      fail "managed state exists but canonical Codex Orchestration is missing; RECOVERY_REQUIRED"
    }
    let native = (native-status $python_bin $dependency.script $codex_bin $codex_home true)
    if not $native.installed or $native.executor.kind != "agent" or $native.executor.agent != $AGENT_NAME {
      fail "managed state exists but the effective Executor route drifted; RECOVERY_REQUIRED"
    }
    print "ALREADY_CONFIGURED"
    return
  }

  let dependency_before = (dependency-status $codex_bin)
  let catalog = (inspect-catalog $paths.source_catalog)
  let needs_shim = ($catalog.multi_agent_version == "v1")
  let generated_content = if $needs_shim { shim-content $catalog } else { null }
  let config_existed = ($paths.config | path exists)
  let config_raw = if $config_existed { open --raw $paths.config } else { "" }
  let config = (config-info $config_raw)
  if $needs_shim and $config.line != null {
    fail "top-level model_catalog_json is not managed by CodexLFE; refusing setup"
  }
  let managed_line = if $needs_shim { managed-catalog-line $paths.generated_catalog } else { null }
  let config_after = if $needs_shim { set-catalog-line $config_raw $config $managed_line } else { $config_raw }
  let expected_agent = (agent-content)
  mut agent_created = true
  if ($paths.agent | path exists) {
    if (open --raw $paths.agent) != $expected_agent {
      fail "codex_lfe_executor already exists with non-CodexLFE content"
    }
    $agent_created = false
  }
  mut generated_created = $needs_shim
  if $needs_shim and ($paths.generated_catalog | path exists) {
    if (open --raw $paths.generated_catalog) != $generated_content {
      fail "CodexLFE generated catalog path already exists with different content"
    }
    $generated_created = false
  }
  if ($paths.restore | path exists) {
    fail "CodexLFE restore snapshot exists without state; RECOVERY_REQUIRED"
  }

  mut dependency = $dependency_before
  mut installed_by_tool = false
  mut marketplace_added_by_tool = false
  if not $dependency.installed {
    let installed = (install-dependency $codex_bin)
    $installed_by_tool = true
    $marketplace_added_by_tool = $installed.marketplace_added
    $dependency = (dependency-status $codex_bin)
    if not $dependency.installed {
      fail "canonical Codex Orchestration was not visible after installation"
    }
  }
  let prior = (native-status $python_bin $dependency.script $codex_bin $codex_home false)
  if $prior.installed and $prior.executor.kind == "agent" and $prior.executor.agent == $AGENT_NAME {
    fail "the native policy already references codex_lfe_executor without CodexLFE state; RECOVERY_REQUIRED"
  }

  print "PREVIEW: create or verify bounded codex_lfe_executor"
  if $needs_shim {
    print $"PREVIEW: generate Luna v2 catalog from ($paths.source_catalog)"
    print $"PREVIEW: set top-level model_catalog_json in ($paths.config)"
  } else {
    print "PREVIEW: Luna is already v2; no catalog shim or config change"
  }
  print "PREVIEW: preserve existing Planner, Advisor, and Designer routes"
  print "PREVIEW: set canonical Orchestration Executor to custom agent codex_lfe_executor"

  let restore_record = {
    schema_version: $STATE_SCHEMA
    owner: "CodexLFE"
    config_path: ($paths.config | into string)
    config_existed_before: $config_existed
    config_before_hash: (if $config_existed { sha-text $config_raw } else { null })
    original_catalog_line: $config.line
    original_catalog_value: $config.value
    original_catalog_line_index: $config.line_index
    newline: $config.newline
    managed_catalog_line: $managed_line
  }
  let restore_content = $"($restore_record | to json --indent 2)(char nl)"
  atomic-save $paths.restore $restore_content
  if $needs_shim {
    atomic-save $paths.generated_catalog $generated_content
    atomic-save $paths.config $config_after
  }
  atomic-save $paths.agent $expected_agent

  mut state = {
    schema_version: $STATE_SCHEMA
    owner: "CodexLFE"
    codex_home: ($codex_home | into string)
    config_path: ($paths.config | into string)
    config_existed_before: $config_existed
    config_before_hash: (if $config_existed { sha-text $config_raw } else { null })
    config_after_hash: (if ($paths.config | path exists) { sha-file $paths.config } else { null })
    original_catalog_line: $config.line
    original_catalog_value: $config.value
    original_catalog_line_index: $config.line_index
    managed_catalog_line: $managed_line
    source_catalog_path: ($paths.source_catalog | into string)
    source_catalog_hash: $catalog.source_hash
    generated_catalog_path: (if $needs_shim { $paths.generated_catalog | into string } else { null })
    generated_catalog_hash: (if $needs_shim { sha-text $generated_content } else { null })
    generated_catalog_created: $generated_created
    custom_agent_path: ($paths.agent | into string)
    custom_agent_hash: (sha-text $expected_agent)
    custom_agent_created: $agent_created
    restore_snapshot_path: ($paths.restore | into string)
    restore_snapshot_hash: (sha-text $restore_content)
    orchestration_installed_by_tool: $installed_by_tool
    orchestration_marketplace_added_by_tool: $marketplace_added_by_tool
    routing_prior_installed: $prior.installed
    routing_prior_executor: $prior.executor
    routing_prior_planner: $prior.planner
    routing_prior_advisor: $prior.advisor
    routing_prior_designer: $prior.designer
    routing_setup_status: "applying"
    restart_required: false
    created_at: (now)
    updated_at: (now)
  }
  atomic-save $paths.state $"($state | to json --indent 2)(char nl)"

  let desired_executor = {kind: "agent", agent: $AGENT_NAME}
  let native_args = (setup-args $dependency.script $codex_bin $codex_home $desired_executor $prior.planner $prior.advisor $prior.designer)
  let dry_run = (run-program $python_bin $native_args)
  if $dry_run.exit_code != 0 {
    $state = ($state | upsert routing_setup_status "failed" | upsert updated_at (now))
    atomic-save $paths.state $"($state | to json --indent 2)(char nl)"
    fail $"canonical routing dry-run failed with exit code ($dry_run.exit_code); RECOVERY_REQUIRED"
  }
  let apply_result = (run-program $python_bin ($native_args | append "--apply"))
  if $apply_result.exit_code != 0 {
    $state = ($state | upsert routing_setup_status "failed" | upsert updated_at (now))
    atomic-save $paths.state $"($state | to json --indent 2)(char nl)"
    fail $"canonical routing apply failed with exit code ($apply_result.exit_code); RECOVERY_REQUIRED"
  }
  let applied = try {
    native-status $python_bin $dependency.script $codex_bin $codex_home true
  } catch {
    null
  }
  if $applied == null or not $applied.installed or $applied.executor.kind != "agent" or $applied.executor.agent != $AGENT_NAME {
    $state = ($state | upsert routing_setup_status "failed" | upsert updated_at (now))
    atomic-save $paths.state $"($state | to json --indent 2)(char nl)"
    fail "canonical routing post-apply readback did not select codex_lfe_executor; RECOVERY_REQUIRED"
  }
  $state = ($state | upsert routing_setup_status "complete" | upsert restart_required true | upsert updated_at (now))
  atomic-save $paths.state $"($state | to json --indent 2)(char nl)"
  print "SETUP_COMPLETE"
  print "RESTART_REQUIRED"
  print "Fully quit Codex, reopen it, and run CodexLFE verify in a new task."
}

def command-verify [codex_home: path, codex_bin: string, python_bin: string, workspace: path] {
  let paths = (state-paths $codex_home)
  if not ($paths.state | path exists) {
    fail "CodexLFE is not configured"
  }
  let state = (load-state $paths.state $codex_home)
  let issues = (inspect-state $state)
  if not ($issues | is-empty) {
    fail $"CodexLFE managed state is unhealthy: ($issues | str join ', '); RECOVERY_REQUIRED"
  }
  let dependency = (dependency-status $codex_bin)
  if not $dependency.installed {
    fail "canonical Codex Orchestration is missing"
  }
  let native = (native-status $python_bin $dependency.script $codex_bin $codex_home true)
  if not $native.installed or $native.executor.kind != "agent" or $native.executor.agent != $AGENT_NAME {
    fail "effective canonical routing does not select codex_lfe_executor"
  }
  let shadows = (find-project-shadows $workspace $paths.agent)
  if not ($shadows | is-empty) {
    fail $"project custom-agent shadowing detected: ($shadows | str join ', ')"
  }
  print "READY_FOR_SPAWN"
  print $"agent_type=($AGENT_NAME)"
  print "fork_turns=none"
  print "Static checks passed. A real exact custom-agent spawn is still required; do not claim the route ran yet."
}

def command-disable [codex_home: path, codex_bin: string, python_bin: string] {
  let paths = (state-paths $codex_home)
  if not ($paths.state | path exists) {
    print "NOT_CONFIGURED"
    return
  }
  let state = (load-state $paths.state $codex_home)
  let issues = (inspect-state $state)
  if not ($issues | is-empty) {
    fail $"CodexLFE managed state drifted: ($issues | str join ', '); refusing disable"
  }
  let dependency = (dependency-status $codex_bin)
  if not $dependency.installed {
    fail "canonical Codex Orchestration is missing; refusing disable"
  }
  let current_native = (native-status $python_bin $dependency.script $codex_bin $codex_home false)
  if not $current_native.installed or $current_native.executor.kind != "agent" or $current_native.executor.agent != $AGENT_NAME {
    fail "canonical Executor route drifted; refusing disable"
  }
  let restore_args = if ($state | get routing_prior_installed) {
    setup-args $dependency.script $codex_bin $codex_home ($state | get routing_prior_executor) ($state | get routing_prior_planner) ($state | get routing_prior_advisor) ($state | get routing_prior_designer)
  } else {
    [($dependency.script | into string) "--codex-bin" $codex_bin "--codex-home" ($codex_home | into string) "--disable"]
  }
  let dry_run = (run-program $python_bin $restore_args)
  if $dry_run.exit_code != 0 {
    fail $"canonical routing restore dry-run failed with exit code ($dry_run.exit_code)"
  }
  print "PREVIEW: restore the exact pre-CodexLFE canonical routing"
  if ($state | get -o managed_catalog_line) != null {
    print "PREVIEW: restore the exact pre-CodexLFE model_catalog_json line"
  }
  if ($state | get custom_agent_created) {
    print $"PREVIEW: remove ($paths.agent)"
  }
  if ($state | get generated_catalog_created) {
    print $"PREVIEW: remove ($paths.generated_catalog)"
  }

  let apply_result = (run-program $python_bin ($restore_args | append "--apply"))
  if $apply_result.exit_code != 0 {
    fail $"canonical routing restore apply failed with exit code ($apply_result.exit_code); RECOVERY_REQUIRED"
  }
  let restoring = ($state | upsert routing_setup_status "restoring_files" | upsert updated_at (now))
  atomic-save $paths.state $"($restoring | to json --indent 2)(char nl)"
  if ($state | get -o managed_catalog_line) != null {
    let current_config = (open --raw $paths.config)
    let restored_config = (restore-catalog-line $current_config $state)
    if ($state | get config_existed_before) {
      atomic-save $paths.config $restored_config
    } else if ($restored_config | is-empty) {
      rm $paths.config
    } else {
      atomic-save $paths.config $restored_config
    }
  }
  if ($state | get custom_agent_created) {
    rm $paths.agent
  }
  if ($state | get generated_catalog_created) {
    rm $paths.generated_catalog
  }
  rm $paths.restore
  rm $paths.state
  print "DISABLE_COMPLETE"
  if ($state | get orchestration_installed_by_tool) {
    print "Canonical Codex Orchestration was retained."
  }
  print "Restart Codex before relying on the restored routing."
}

def main [
  command: string
  --codex-home: path
  --codex-bin: string = "codex"
  --python-bin: string = "python"
  --workspace: path
] {
  let resolved_home = (resolve-codex-home $codex_home)
  let resolved_workspace = if $workspace == null { pwd } else { $workspace | path expand }
  match $command {
    "setup" => { command-setup $resolved_home $codex_bin $python_bin }
    "status" => { command-status $resolved_home $codex_bin $python_bin }
    "disable" => { command-disable $resolved_home $codex_bin $python_bin }
    "verify" => { command-verify $resolved_home $codex_bin $python_bin $resolved_workspace }
    _ => { fail "usage: codex-lfe.nu setup|status|disable|verify" }
  }
}
