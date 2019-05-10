package main


func main() {
    app := App{}
    app.Init("matchessas.db")
    defer app.DB.Close()
    app.Run(":8080")
}
