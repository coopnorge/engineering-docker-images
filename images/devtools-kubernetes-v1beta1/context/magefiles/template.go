//go:build mage
// +build mage

package main

import (
	"fmt"
	"github.com/magefile/mage/sh" // sh contains helpful utility functions, like RunV
	"os"
	"path/filepath"
	"strings"
)

func renderTemplate(app ArgoCDApp) (string, error) {
	if app.Spec.Source.Helm.ReleaseName != "" {
		return renderHelm(app.Spec.Source)
	} else if _, err := os.Stat(app.Spec.Source.Path + "/kustomize.yaml"); err == nil {
		return renderKustomize(app.Spec.Source.Helm.ReleaseName)
	} else {
		return app.Spec.Source.Path, nil
	}
}

func renderHelm(source ArgoCDAppSource) (string, error) {
	dir, err := tempDir()
	if err != nil {
		return "", err
	}
	pwd, _ := os.Getwd()
	os.Chdir(source.Path)
	fmt.Println("rendering helm templates to: " + dir)
	err = sh.Run("helm", "dependency", "build")
	if err != nil {
		return "", err
	}
	err = sh.Run("helm", "template",
		"-f", strings.Join(source.Helm.ValueFiles, ","),
		"--output-dir", dir,
		".")
	if err != nil {
		return "", err
	}
	os.Chdir(pwd)
	return dir, nil
}

func renderKustomize(path string) (string, error) {
	dir, err := tempDir()
	if err != nil {
		return "", err
	}
	fmt.Println("rendering kustomize templates: " + dir)
	err = sh.Run("kustomize", "build", path, "--output", dir)
	if err != nil {
		return "", err
	}
	return dir, nil
}

// Render templates to an temporary directory. Using a comma sep string here because
// mg. can only have int, str and bools as arguments
func renderTemplates() (string, error) {
	var files []string
	repoUrl, err := repoUrl()
	if err != nil {
		return "", err
	}
	apps, err := getArgoCDDeployments(repoUrl)
	if err != nil {
		return "", err
	}
	for _, trackedDeployment := range apps {
		templates, err := renderTemplate(trackedDeployment)
		if err != nil {
			return "", err
		}
		files = append(listFilesInDirectory(templates))
	}
	return strings.Join(files, ","), nil
}

func listFilesInDirectory(path string) []string {
	var files []string
	filepath.Walk(path, func(path string, info os.FileInfo, err error) error {
		if !info.IsDir() {
			files = append(files, path)
		}
		return nil
	})
	return files
}

func tempDir() (string, error) {
	dir, err := os.MkdirTemp("", "kubernetes-validation-*")
	if err != nil {
		return "", err
	}
	return dir, nil
}
