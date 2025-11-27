package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
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

func fetchHandler(w http.ResponseWriter, r *http.Request) {
	userID := r.URL.Query().Get("userid")
	if userID == "" {
		http.Error(w, "user id is needed", http.StatusBadRequest)
	}
	log.Printf("receive request: %s\n", userID)

	subjectIDs, err := fetch(userID)
	if errors.Is(err, bangumi.ErrInvalidUserID) {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]any {
			"error": "invalid userid",
		})
		return
	}
	if err != nil {
		http.Error(w, "internal server error", http.StatusInternalServerError)
	}
	log.Printf("%s count: %d\n", userID, len(subjectIDs))

	json.NewEncoder(w).Encode(map[string]any{
		"subjectIDs": subjectIDs,
	})
}

func proxyHandler(w http.ResponseWriter, r *http.Request) {
    imageURL := r.URL.Query().Get("url")
    if imageURL == "" {
        http.Error(w, `{"error": "url is required"}`, http.StatusBadRequest)
        return
    }

    // 请求远端图片
    resp, err := http.Get(imageURL)
    if err != nil {
        // 返回 JSON 错误
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(map[string]any{
            "error": err.Error(),
        })
        return
    }
    defer resp.Body.Close()

    // 非 200 状态码视为错误
    if resp.StatusCode != http.StatusOK {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(map[string]any{
            "error": fmt.Sprintf("remote server returned status %d", resp.StatusCode),
        })
        return
    }

    // 设置 Content-Type（如果有）
    if ct := resp.Header.Get("Content-Type"); ct != "" {
        w.Header().Set("Content-Type", ct)
    }

    // 把远端内容直接复制给前端（stream）
    _, err = io.Copy(w, resp.Body)
    if err != nil {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(map[string]any{
            "error": err.Error(),
        })
        return
    }
}

func withCORS(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // CORS headers
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

        // Preflight OPTIONS request
        if r.Method == http.MethodOptions {
            return
        }

        next.ServeHTTP(w, r)
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

    mux := http.NewServeMux()
    mux.HandleFunc("/2025", fetchHandler)
    mux.HandleFunc("/proxy", proxyHandler)

    handler := withCORS(mux)

    if err := http.ListenAndServe(":2025", handler); err != nil {
        panic(err)
    }
}
