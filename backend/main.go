package main

import (
	"context"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/AcuLY/Annual-Top3/backend/bangumi"
	"golang.org/x/sync/errgroup"
)

func fetch(userID string) ([]int, error) {
	g := new(errgroup.Group)
	var m sync.Mutex
	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()

	subjectIDs := make([]int, 0)

	for i := 2; i <= 5; i++ {
		query := bangumi.CollectionQuery{
			UserID: userID,
			SubjectType: 2,
			CollectionType: i,
		}

		g.Go(func() error {
			result, err := bangumi.FetchCollections(ctx, query)
			if err != nil {
				return err
			}

			m.Lock()
			defer m.Unlock()

			for _, c := range result {
				if c.Subject.Date < "2025-01-01" || c.Subject.Date > "2025-12-31" {
					continue
				}
				subjectIDs = append(subjectIDs, c.SubjectID)
			}

			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}

	return subjectIDs, nil
}

func handler(w http.ResponseWriter, r *http.Request) {
	userID := r.URL.Query().Get("userid")
	if userID == "" {
		http.Error(w, "user id is needed", http.StatusBadRequest)
	}
	log.Printf("receive request: %s\n", userID)

	subjectIDs, err := fetch(userID)
	if err != nil {
		http.Error(w, "internal server error", http.StatusInternalServerError)
	}
	log.Printf("%s count: %d\n", userID, len(subjectIDs))

	json.NewEncoder(w).Encode(map[string]any{
		"subjectIDs": subjectIDs,
	})
}

func main() {
	f, err := os.OpenFile("app.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(err)
	}

	multi := io.MultiWriter(os.Stdout, f)
	log.SetOutput(multi)
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	log.Println("server started")
	http.HandleFunc("/2025", handler)

	if err := http.ListenAndServe(":2025", nil); err != nil {
		panic(err)
	}
}