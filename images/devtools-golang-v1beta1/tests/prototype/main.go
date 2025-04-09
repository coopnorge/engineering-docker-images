package main

import (
	"errors"
	"fmt"
	"os"

	"example.com/prototype/sum"
)

func main() {
	fmt.Println("2 + 2 =", sum.Sum(2, 2))
	fmt.Println("os.Args =", os.Args)

	err := badError()
	if err != nil {
		panic(err)
	}

	err = goodError()
	if err != nil {
		panic(err)
	}
}

func badError() error {
	return errors.New("This is an error") //nolint:stylecheck
}

func goodError() error {
	return errors.New("this is an error")
}
