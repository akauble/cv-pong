package main

import (
	"encoding/json"
	"github.com/boltdb/bolt"
	"github.com/gorilla/mux"
	"github.com/pkg/errors"
	"strconv"
	"time"
)

type Match struct {
	Id	int	`json:"id"`
	Timestamp time.Time `json:"time"`
	P1name string `json:"p1name"`
	P2name string `json:"p2name"`
	P1score int `json:"p1score"`
	P2score int `json:"p2score"`
}

func getMatch(db *bolt.DB, id int) (Match, error) {
	match := Match{}
	err := db.View(func(tx *bolt.Tx) error {
		bk := tx.Bucket([]byte("matches"))
		if bk == nil {
			return errors.Wrapf(bolt.ErrBucketNotFound, "failed to open matches bucket")
		}
		matchjson := []byte(bk.Get([]byte(strconv.Itoa(id))))
		if matchjson == nil {
			return errors.Wrapf(mux.ErrNotFound, "no match found")
		}
		err := json.Unmarshal(matchjson, &match)
		if err != nil {
			return errors.Wrapf(err, "retrieved invalid match from db")
		}
		return nil
	})
	if err != nil {
		return match, err
	}
	return match, nil
}

func updateMatch(db *bolt.DB, id int, p1score int, p2score int) error {
	err := db.Update(func(tx *bolt.Tx) error {
		bk, err := tx.CreateBucketIfNotExists([]byte("matches"))
		if err != nil {
			return errors.Wrapf(err, "error opening bucket for modification")
		}

		matchjson := bk.Get([]byte(strconv.Itoa(id)))
		if matchjson == nil {
			return errors.Wrapf(mux.ErrNotFound, "no match found")
		}
		match := Match{}
		err = json.Unmarshal(matchjson, &match)
		if err != nil {
			return errors.Wrapf(err, "retrieved invalid match from db")
		}

		match.P1score = p1score
		match.P2score = p2score

		matchjson, err = json.Marshal(match)
		if err != nil {
			return errors.Wrapf(err, "error serializing modified match")
		}

		err = bk.Put([]byte(strconv.Itoa(id)), matchjson)
		if err != nil {
			return errors.Wrapf(err, "error storing modified match")
		}
		return nil
	})
	if err != nil {
		return err
	}
	return nil
}

func createMatch(db *bolt.DB, p1name string, p2name string) (int, error) {
	id := 0
	err := db.Update(func(tx *bolt.Tx) error {
		bk, err := tx.CreateBucketIfNotExists([]byte("matches"))
		if err != nil {
			return errors.Wrapf(err, "error opening bucket for modification")
		}

		matchid := 1;
		if bk.Stats().KeyN != 0 {
			/*k, _ := bk.Cursor().Last()
			k, _ = bk.Cursor().Last()
			fmt.Println("keyn")
			fmt.Println(bk.Stats().KeyN)
			lastid, _ := strconv.Atoi(string(k))
			fmt.Println("lastid")
			fmt.Println(lastid)*/
			matchid = bk.Stats().KeyN+1
		}

		match := Match{Id: matchid, P1name: p1name, P2name: p2name, P1score: 0, P2score: 0, Timestamp: time.Now()}
		matchjson, err := json.Marshal(match)
		if err != nil {
			return errors.Wrapf(err, "error serializing new match")
		}
		err = bk.Put([]byte(strconv.Itoa(matchid)), matchjson)
		if err != nil {
			return errors.Wrapf(err, "error storing new match")
		}

		id = matchid
		return nil
	})
	if err != nil {
		return id, err
	}
	return id, nil
}

func getMatches(db *bolt.DB) ([]Match, error) {
	matches := []Match{}
	err := db.View(func(tx *bolt.Tx) error {
		bk := tx.Bucket([]byte("matches"))
		if bk == nil {
			return errors.Wrapf(bolt.ErrBucketNotFound, "failed to open matches bucket")
		}
		c := bk.Cursor()
		for k, v := c.First(); k != nil; k, v = c.Next() {
			data := []byte(v)
			var match Match
			err := json.Unmarshal(data, &match)
			if err != nil {
				return errors.Wrapf(err, "encountered malformed match with id " + string(k))
			}
			matches = append(matches, match)
		}
		return nil
	})

	if err != nil {
		return matches, err
	}
	return matches, nil
}