package main


func main() {
    app := App{}
    app.Init("matches.db")
    app.Run(":80")
}
