package main

import (
	"encoding/json"
	"fmt"
	"github.com/boltdb/bolt"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"sort"
	"strconv"
	"github.com/unrolled/render"
)

type App struct {
	Router *mux.Router
	DB *bolt.DB
	Render *render.Render
}

func (app *App) Init(dbname string) {
	db, err := bolt.Open(dbname, 0600, nil)
	if err != nil {
		log.Fatal(err)
	}
	//defer db.Close()
	app.DB = db
	app.Router = mux.NewRouter()
	app.Render = render.New()
	app.InitRoutes()
}

func (app *App) Run(address string) {
	log.Fatal(http.ListenAndServe(address, app.Router))
}

func (app *App) InitRoutes() {
	app.Router.HandleFunc("/match", app.createMatch).Methods("POST")
	app.Router.HandleFunc("/match", app.getMatches).Methods("GET")
	app.Router.HandleFunc("/match/{id:[0-9]+}", app.updateMatch).Methods("POST")
	app.Router.HandleFunc("/match/{id:[0-9]+}", app.getMatch).Methods("GET")
	app.Router.HandleFunc("/", app.webView)
	app.Router.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
}

func (app *App) createMatch(w http.ResponseWriter, r *http.Request) {
	urlparams := r.URL.Query()
	p1name, p2name := urlparams["p1name"], urlparams["p2name"]
	fmt.Println(p1name, p2name)
	id, err := createMatch(app.DB, p1name[0], p2name[0])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, err.Error())
		return
	}
	fmt.Printf("New match created for %s and %s with id %d\n", p1name, p2name, id)
	respondWithJSON(w, http.StatusOK, map[string]int{"id": id})
}

func (app *App) updateMatch(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	urlparams := r.URL.Query()
	p1score, err := strconv.Atoi(urlparams["p1score"][0])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
		return
	}
	p2score, err := strconv.Atoi(urlparams["p2score"][0])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
		return
	}
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid parameters")
		return
	}
	err = updateMatch(app.DB, id, p1score, p2score)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	fmt.Printf("Match %d updated with score %d %d", id, p1score, p2score)

}

func (app *App) getMatch(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])
	match, err := getMatch(app.DB, id)
	if err != nil {
		fmt.Println(err.Error())
	}
	fmt.Printf("ID: %d P1: %s-%d P2: %s-%d", match.Id, match.P1name, match.P1score, match.P2name, match.P2score)
	json, err := json.Marshal(match)
	if err != nil {
		respondWithError(w, 500, err.Error())
	}
	respondWithJSON(w, 200, string(json))
}

func (app *App) getMatches(w http.ResponseWriter, r *http.Request) {
	matches, err := getMatches(app.DB)
	if err != nil {
		respondWithError(w, 500, err.Error())
	}

	json, err := json.Marshal(matches)
	if err != nil {
		respondWithError(w, 500, err.Error())
	}
	respondWithJSON(w, 200, string(json))
}

func (app *App) webView(w http.ResponseWriter, r *http.Request) {
	matches, err := getMatches(app.DB)
	i := 0
	for _, match := range matches {
		if !(match.P1score == 0 && match.P2score == 0) {
			matches[i] = match
			i++
		}
	}
	matches = matches[:i]
	sort.Slice(matches, func(i, j int) bool { return matches[i].Timestamp.After(matches[j].Timestamp )})
	if err != nil {
		respondWithError(w, 500, err.Error())
	}
	app.Render.HTML(w, http.StatusOK, "index", matches)
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