package term

import "os"

var IsRepl = os.Getenv("LLMCODE_REPL") != ""

func SetIsRepl(value bool) {
	IsRepl = value
}
