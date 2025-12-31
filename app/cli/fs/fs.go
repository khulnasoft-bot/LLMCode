package fs

import (
	"os"
	"os/exec"
	"path/filepath"
	"llmcode/term"
)

var Cwd string
var LlmcodeDir string
var ProjectRoot string
var HomeLlmcodeDir string
var CacheDir string

var HomeDir string
var HomeAuthPath string
var HomeAccountsPath string

func init() {
	var err error
	Cwd, err = os.Getwd()
	if err != nil {
		term.OutputErrorAndExit("Error getting current working directory: %v", err)
	}

	home, err := os.UserHomeDir()
	if err != nil {
		term.OutputErrorAndExit("Couldn't find home dir: %v", err.Error())
	}
	HomeDir = home

	if os.Getenv("LLMCODE_ENV") == "development" {
		HomeLlmcodeDir = filepath.Join(home, ".llmcode-home-dev-v2")
	} else {
		HomeLlmcodeDir = filepath.Join(home, ".llmcode-home-v2")
	}

	// Create the home llmcode directory if it doesn't exist
	err = os.MkdirAll(HomeLlmcodeDir, os.ModePerm)
	if err != nil {
		term.OutputErrorAndExit(err.Error())
	}

	CacheDir = filepath.Join(HomeLlmcodeDir, "cache")
	HomeAuthPath = filepath.Join(HomeLlmcodeDir, "auth.json")
	HomeAccountsPath = filepath.Join(HomeLlmcodeDir, "accounts.json")

	err = os.MkdirAll(filepath.Join(CacheDir, "tiktoken"), os.ModePerm)
	if err != nil {
		term.OutputErrorAndExit(err.Error())
	}
	err = os.Setenv("TIKTOKEN_CACHE_DIR", CacheDir)
	if err != nil {
		term.OutputErrorAndExit(err.Error())
	}

	FindLlmcodeDir()
	if LlmcodeDir != "" {
		ProjectRoot = Cwd
	}
}

func FindOrCreateLlmcode() (string, bool, error) {
	FindLlmcodeDir()
	if LlmcodeDir != "" {
		ProjectRoot = Cwd
		return LlmcodeDir, false, nil
	}

	// Determine the directory path
	var dir string
	if os.Getenv("LLMCODE_ENV") == "development" {
		dir = filepath.Join(Cwd, ".llmcode-dev-v2")
	} else {
		dir = filepath.Join(Cwd, ".llmcode-v2")
	}

	err := os.Mkdir(dir, os.ModePerm)
	if err != nil {
		return "", false, err
	}
	LlmcodeDir = dir
	ProjectRoot = Cwd

	return dir, true, nil
}

func ProjectRootIsGitRepo() bool {
	if ProjectRoot == "" {
		return false
	}

	return IsGitRepo(ProjectRoot)
}

func IsGitRepo(dir string) bool {
	isGitRepo := false

	if isCommandAvailable("git") {
		// check whether we're in a git repo
		cmd := exec.Command("git", "rev-parse", "--is-inside-work-tree")

		cmd.Dir = dir

		err := cmd.Run()

		if err == nil {
			isGitRepo = true
		}
	}

	return isGitRepo
}

func FindLlmcodeDir() {
	LlmcodeDir = findLlmcode(Cwd)
}

func findLlmcode(baseDir string) string {
	var dir string
	if os.Getenv("LLMCODE_ENV") == "development" {
		dir = filepath.Join(baseDir, ".llmcode-dev-v2")
	} else {
		dir = filepath.Join(baseDir, ".llmcode-v2")
	}
	if _, err := os.Stat(dir); !os.IsNotExist(err) {
		return dir
	}

	return ""
}

func isCommandAvailable(name string) bool {
	cmd := exec.Command(name, "--version")
	if err := cmd.Run(); err != nil {
		return false
	}
	return true
}
