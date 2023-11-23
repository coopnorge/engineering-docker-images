//go:build mage
// +build mage

package main

import (
	"fmt"
	"github.com/magefile/mage/sh" // sh contains helpful utility functions, like RunV
	"gopkg.in/yaml.v3"
	"os"
	"strings"
)

type ArgoCDAppHelm struct {
	ReleaseName string   `yaml:"releaseName"`
	ValueFiles  []string `yaml:"valueFiles"`
}

type ArgoCDAppSource struct {
	Helm ArgoCDAppHelm `yaml:"helm"`
	Path string        `yaml:"path"`
}

type ArgoCDAppSpec struct {
	Source ArgoCDAppSource `yaml:"source"`
}

type ArgoCDAppMetadata struct {
	Name string `yaml:"name"`
}

type ArgoCDApp struct {
	Spec     ArgoCDAppSpec     `yaml:"spec"`
	Metadata ArgoCDAppMetadata `yaml:"metadata"`
}

func getArgoCDDeployments(repoURL string) ([]ArgoCDApp, error) {
	var argoCDAppList []ArgoCDApp
	env := map[string]string{}
	if token, ok := os.LookupEnv("ARGOCD_API_TOKEN"); ok {
		env["ARGOCD_API_TOKEN"] = token
	}
	appYaml, err := sh.OutputWith(env, "argocd", "--grpc-web", "app", "list", "-r", repoURL, "-o", "yaml")
	if err != nil {
		return nil, err
	}
	yaml.Unmarshal([]byte(appYaml), &argoCDAppList)
	return argoCDAppList, nil
}

func getArgoCDDiff(apps []ArgoCDApp) error {
	env := map[string]string{"KUBECTL_EXTERNAL_DIFF": "dyff between --omit-header"}
	if token, ok := os.LookupEnv("ARGOCD_API_TOKEN"); ok {
		env["ARGOCD_API_TOKEN"] = token
	}
	for _, app := range apps {
		diff, err := sh.OutputWith(env, "argocd", "--loglevel", "error", "--grpc-web", "app", "diff", app.Metadata.Name, "--refresh", "--local", app.Spec.Source.Path)
		if sh.ExitStatus(err) == 2 {
			return err
		}
		fmt.Println("---- Diff of " + app.Metadata.Name + "  ----")
		fmt.Println(diff)
	}
	return nil
}

func listArgoCDDeployments() error {
	repoUrl, err := repoUrl()
	if err != nil {
		return err
	}
	apps, err := getArgoCDDeployments(repoUrl)
	if err != nil {
		return err
	}
	for _, trackedDeployment := range apps {
		if trackedDeployment.Spec.Source.Helm.ReleaseName != "" {
			fmt.Println("---")
			fmt.Println("Found helm deployment with name: " + trackedDeployment.Metadata.Name)
			fmt.Println("  path: " + trackedDeployment.Spec.Source.Path)
			fmt.Println("  valueFiles: " + strings.Join(trackedDeployment.Spec.Source.Helm.ValueFiles, ", "))
		} else if _, err := os.Stat(trackedDeployment.Spec.Source.Path + "/kustomize.yaml"); err == nil {
			fmt.Println("---")
			fmt.Println("Found kustomize deployment with name: " + trackedDeployment.Metadata.Name)
			fmt.Println("  path: " + trackedDeployment.Spec.Source.Path)
		} else {
			fmt.Println("---")
			fmt.Println("Found plain deployment with name: " + trackedDeployment.Metadata.Name)
			fmt.Println("  path: " + trackedDeployment.Spec.Source.Path)
		}
	}
	return nil
}
