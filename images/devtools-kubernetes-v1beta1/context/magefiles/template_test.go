//go:build mage
// +build mage

package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestListFilesInDir(t *testing.T) {
	dir := "tests/listfiles"
	want := []string{"tests/listfiles/a.yaml", "tests/listfiles/dir/b.yaml"}
	out := listFilesInDirectory(dir)
	if !testStringSliceEq(out, want) {
		t.Fatalf(`listFilesInDirectory(dir) = %q, want match for %q`, out, want)
	}
}

func TestTempDir(t *testing.T) {
	dir, err := tempDir()
	_, staterr := os.Stat(dir)
	if err != nil || staterr != nil {
		t.Fatalf(`tempDir() failed. %v %v`, err, staterr)
	}
}

func TestOkRenderKustomize(t *testing.T) {
	out, err := renderKustomize("tests/kustomize/overlay/production")
	_, staterr := os.Stat(filepath.Join(out, "apps_v1_deployment_helloworld.yaml"))
	if err != nil || staterr != nil {
		t.Fatalf(`renderKustomize("tests/kustomize/overlay/production") returned an error %v or %v`, err, staterr)
	}
}

func TestFailRenderKustomize(t *testing.T) {
	out, err := renderKustomize("tests/kustomize/fail")
	if err == nil {
		t.Fatalf(`renderKustomize("tests/kustomize/overlay/fail") should return an error but returned ok status %v`, out)
	}
}

func TestOkRenderHelm(t *testing.T) {
	appSource := &ArgoCDAppSource{
		Path: "tests/helm/ok",
		Helm: ArgoCDAppHelm{
			ReleaseName: "test",
			ValueFiles:  []string{"values.yaml"},
		},
	}
	out, err := renderHelm(*appSource)
	_, staterr := os.Stat(filepath.Join(out, "ok", "templates", "deployment.yaml"))
	if err != nil || staterr != nil {
		t.Fatalf(`renderHelm("tests/helm/ok") returned an error %v or %v`, err, staterr)
	}
}

func TestFailRenderHelm(t *testing.T) {
	appSource := &ArgoCDAppSource{
		Path: "tests/helm/fail",
		Helm: ArgoCDAppHelm{
			ReleaseName: "test",
			ValueFiles:  []string{"values.yaml"},
		},
	}
	out, err := renderHelm(*appSource)
	if err == nil {
		t.Fatalf(`renderKustomize("tests/helm/fail") should return an error but returned ok status %v`, out)
	}
}

//// TestHelloEmpty calls greetings.Hello with an empty string,
//// checking for an error.
//func TestHelloEmpty(t *testing.T) {
//    msg, err := Hello("")
//    if msg != "" || err == nil {
//        t.Fatalf(`Hello("") = %q, %v, want "", error`, msg, err)
//    }
//}

func testStringSliceEq(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
