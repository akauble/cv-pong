package main

import (
	"encoding/json"
	"github.com/boltdb/bolt"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"strconv"
)

type App struct {
	Router *mux.Router
	DB *bolt.DB
}

func (app *App) Init(dbname string) {
	db, err := bolt.Open(dbname, 0600, nil)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	app.DB = db
	app.Router = mux.NewRouter()
}

func (app *App) Run(address string) {
	log.Fatal(http.ListenAndServe(address, app.Router))
}

func (app *App) InitRoutes() {
	app.Router.HandleFunc("/match", app.createMatch).Methods("POST")
	app.Router.HandleFunc("/match/{id:[0-9]+}", app.updateMatch).Methods("POST")

}

func (app *App) createMatch(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	p1name, p2name := vars["p1name"], vars["p2name"]
	id, err := createMatch(app.DB, p1name, p2name)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Failed to create match")
	}
	respondWithJSON(w, http.StatusOK, map[string]int{"id": id})
}

func (app *App) updateMatch(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	p1score, err := strconv.Atoi(vars["p1score"])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
	}
	p2score, err := strconv.Atoi(vars["p2score"])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
	}
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
	}
	err = updateMatch(app.DB, id, p1score, p2score)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
	}
}


func respondWithError(w http.ResponseWriter, code int, message string) {
	respondWithJSON(w, code, map[string]string{"err": message})
}

func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}