//go:build tools
// +build tools

package root

//nolint:golint
import (
	_ "github.com/abice/go-enum"                                          // toolchain
	_ "github.com/cortesi/modd/cmd/modd"                                  // toolchain
	_ "github.com/envoyproxy/protoc-gen-validate"                         // toolchain
	_ "github.com/go-delve/delve/cmd/dlv"                                 // toolchain
	_ "github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway" // toolchain
	_ "github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2"    // toolchain
	_ "github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc"           // toolchain
	_ "github.com/sanposhiho/gomockhandler"                               // toolchain
	_ "go.uber.org/mock/mockgen"                                          // toolchain
	_ "google.golang.org/grpc/cmd/protoc-gen-go-grpc"                     // toolchain
	_ "google.golang.org/protobuf/cmd/protoc-gen-go"                      // toolchain
)
