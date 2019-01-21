package main

import (
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"strings"
)

type ss struct {
	S []string    `json:"s"`
	I []int       `json:"i"`
	A interface{} `json:"a"`
}

type uappXml struct {
	XMLName    xml.Name `xml:"uapp"`
	Version    string   `xml:"version"`
	Bundleid   string   `xml:"bundleid"`
	Name       string   `xml:"name"`
	Versionlog string   `xml:"versionlog"`
	Box        boxXml   `xml:"box"`
}

type boxXml struct {
	Packageurl string `xml:"packageurl"`
	Md5        string `xml:"md5"`
}

func main() {
	b, _ := ioutil.ReadFile("/Users/licoyqtc/GoglandProjects/src/cf3/a.xml")

	x := uappXml{}
	xml.Unmarshal(b, &x)

	url := "http://iamtest.yqtc.co/Application/com.pvr.www/com.pvr.www.xml"

	index := 0
	for i := len(url) - 1; i > 0; i-- {
		if url[i] == '/' {
			index = i
			break
		}
	}

	prefix := "./com.pvr.www.tar"
	s := strings.Replace(prefix, "./", "/", -1)
	fmt.Println(s)

	fmt.Println(url[:index])
	p := url[:index] + s

	fmt.Println(p)
}
