//go:build mage
// +build mage

package main

import (
	"fmt"
	"gopkg.in/yaml.v3"
	"io/ioutil"
)

type Annotations struct {
	ProjectSlug string `yaml:"github.com/project-slug"`
}

type Metadata struct {
	Annotations Annotations `yaml:"annotations"`
}

type CatalogInfo struct {
	Metadata Metadata `yaml:"metadata"`
}

func repoName() (string, error) {
	var catalogInfo CatalogInfo

	yamlFile, err := ioutil.ReadFile("catalog-info.yaml")
	if err != nil {
		fmt.Printf("yamlFile.Get err #%v ", err)
		return "", err
	}
	err = yaml.Unmarshal(yamlFile, &catalogInfo)
	if err != nil {
		fmt.Printf("Unmarshal: %v", err)
		return "", err
	}
	return catalogInfo.Metadata.Annotations.ProjectSlug, nil
}

func repoUrl() (string, error) {
	repoName, err := repoName()
	if err != nil {
		return "", err
	}
	return "https://github.com/" + repoName, nil
}
