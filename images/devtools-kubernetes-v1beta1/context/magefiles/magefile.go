//go:build mage
// +build mage

package main

import (
	"fmt"
	"github.com/magefile/mage/mg" // mg contains helpful utility functions, like Deps
	"github.com/magefile/mage/sh" // sh contains helpful utility functions, like RunV
	"strings"
)

// Validate Kubernetes manifests for ArgCD applications related to this repository
func Validate() {
	templates, _ := renderTemplates()
	mg.Deps(mg.F(kubeScore, templates))
	mg.Deps(mg.F(kubeConform, templates))
	fmt.Println("Validation passed")
}

// Run kube-score  on Kubernetes manifests for ArgCD applications related to this repository
func KubeScore() error {
	templates, err := renderTemplates()
	if err != nil {
		return err
	}
	return kubeScore(templates)
}

// Run kubeconform on Kubernetes manifests for ArgCD applications related to this repository
func KubeConform() error {
	templates, err := renderTemplates()
	if err != nil {
		return err
	}
	return kubeConform(templates)
}

// List ArgoCD Apps related to this repository
func ArgoCDListApps() {
	listArgoCDDeployments()
}

// Run a diff between local changes and the current running state in ArgoCD
func ArgoCDDiff() error {
	repoUrl, err := repoUrl()
	if err != nil {
		return err
	}
	apps, err := getArgoCDDeployments(repoUrl)
	if err != nil {
		return err
	}
	err = getArgoCDDiff(apps)
	if err != nil {
		return err
	}
	return nil
}

func kubeScore(paths string) error {
	cmdOptions := []string{
		"score"}
	out, err := sh.Output("kube-score", append(cmdOptions, strings.Split(paths, ",")...)...)
	if err != nil {
		fmt.Printf("kube-score returned exit code: %d\n Output:\n %v Error:\n %v\n", sh.ExitStatus(err), out, err)
		return err
	} else {
		fmt.Println("kube-score passed")
	}
	return nil
}

func kubeConform(paths string) error {
	cmdOptions := []string{
		"-strict",
		"-verbose",
		"-ignore-missing-schemas",
		"-schema-location", "default",
		"-schema-location", "https://raw.githubusercontent.com/coopnorge/kubernetes-schemas/main/api-production/'{{ .ResourceKind }}{{ .KindSuffix }}.json'"}
	out, err := sh.Output("kubeconform", append(cmdOptions, strings.Split(paths, ",")...)...)
	if err != nil {
		fmt.Printf("kubeconform returned exit code: %d\n Output:\n %v Error:\n %v\n", sh.ExitStatus(err), out, err)
		return err
	} else {
		fmt.Println("kubeconform passed")
	}
	return nil
}
