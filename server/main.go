package main

import (
//    "encoding/json"
    "log"
    "net/http"
//    "html/template"
    "github.com/gorilla/mux"
)

func main() {
    router := mux.NewRouter()
    log.Fatal(http.ListenAndServe(":80", router))
}
