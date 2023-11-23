//go:build tools
// +build tools

package root

//nolint:golint
import (
	_ "github.com/magefile/mage"                                // toolchain
	_ "github.com/homeport/dyff/cmd/dyff"                       // toolchain
)
