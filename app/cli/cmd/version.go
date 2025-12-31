package cmd

import (
	"fmt"

	"llmcode/version"

	"github.com/spf13/cobra"
)

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print the version number of Llmcode",
	Long:  `All software has versions. This is Llmcode's`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println(version.Version)
	},
}

func init() {
	RootCmd.AddCommand(versionCmd)
}
