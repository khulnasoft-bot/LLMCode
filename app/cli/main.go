package main

import (
	"log"
	"os"
	"path/filepath"
	"llmcode/api"
	"llmcode/auth"
	"llmcode/cmd"
	"llmcode/fs"
	"llmcode/lib"
	"llmcode/plan_exec"
	"llmcode/term"
	"llmcode/types"
	"llmcode/ui"

	shared "llmcode-shared"

	"gopkg.in/natefinch/lumberjack.v2"
)

func init() {
	// inter-package dependency injections to avoid circular imports
	auth.SetApiClient(api.Client)

	auth.SetOpenUnauthenticatedCloudURLFn(ui.OpenUnauthenticatedCloudURL)
	auth.SetOpenAuthenticatedURLFn(ui.OpenAuthenticatedURL)

	term.SetOpenAuthenticatedURLFn(ui.OpenAuthenticatedURL)
	term.SetOpenUnauthenticatedCloudURLFn(ui.OpenUnauthenticatedCloudURL)
	term.SetConvertTrialFn(auth.ConvertTrial)

	lib.SetBuildPlanInlineFn(func(autoConfirm bool, maybeContexts []*shared.Context) (bool, error) {
		var apiKeys map[string]string
		if !auth.Current.IntegratedModelsMode {
			apiKeys = lib.MustVerifyApiKeys()
		}
		return plan_exec.Build(plan_exec.ExecParams{
			CurrentPlanId: lib.CurrentPlanId,
			CurrentBranch: lib.CurrentBranch,
			ApiKeys:       apiKeys,
			CheckOutdatedContext: func(maybeContexts []*shared.Context, projectPaths *types.ProjectPaths) (bool, bool, error) {
				return lib.CheckOutdatedContextWithOutput(true, autoConfirm, maybeContexts, projectPaths)
			},
		}, types.BuildFlags{})
	})

	// set up a rotating file logger
	logger := &lumberjack.Logger{
		Filename:   filepath.Join(fs.HomeLlmcodeDir, "llmcode.log"),
		MaxSize:    10,   // megabytes before rotation
		MaxBackups: 3,    // number of backups to keep
		MaxAge:     28,   // days to keep old logs
		Compress:   true, // compress rotated files
	}

	// Set the output of the logger
	log.SetOutput(logger)
	log.SetFlags(log.LstdFlags | log.Lmicroseconds | log.Lshortfile)

	// log.Println("Starting Llmcode - logging initialized")
}

func main() {
	// Manually check for help flags at the root level
	if len(os.Args) == 2 && (os.Args[1] == "-h" || os.Args[1] == "--help") {
		// Display your custom help here
		term.PrintCustomHelp(true)
		os.Exit(0)
	}

	var firstArg string
	if len(os.Args) > 1 {
		firstArg = os.Args[1]
	}

	if firstArg != "version" && firstArg != "browser" && firstArg != "help" && firstArg != "h" {
		checkForUpgrade()
	}

	cmd.Execute()
}
