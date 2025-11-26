package httpclient

import (
	"context"
	"errors"
	"net/http"
	"net/url"
	"time"

	"golang.org/x/time/rate"
)

var (
	limiter          *rate.Limiter
	client           *http.Client
	maxRetries             = 3
	retryWaitTime          = 3
	userAgent = "AcuL/Annual-Top3/1.0 (Web) (https://github.com/AcuLY/Annual-Top3)"
	ErrNetworkFailed error = errors.New("network failed")
)

func init() {
	limiter = rate.NewLimiter(5, 10)
	client = &http.Client{Timeout: time.Minute}
}

// GET 发送 GET 请求，并进行速率限制。
func GET(ctx context.Context, baseURL string, params map[string][]string) (*http.Response, error) {
	fullURL := baseURL + "?" + url.Values(params).Encode()
	var resp *http.Response

	for i := range maxRetries {
		err := limiter.Wait(ctx)
		if err != nil {
			return nil, ErrNetworkFailed
		}

		req, err := http.NewRequestWithContext(ctx, "GET", fullURL, nil)
		if err != nil {
			return nil, ErrNetworkFailed
		}

		req.Header.Set("User-Agent", userAgent)
		resp, err = client.Do(req)

		// 等待并重试
		if err != nil {
			waitTime := retryWaitTime * (i + 1)
			select {
			case <-ctx.Done():
				return nil, ErrNetworkFailed
			case <-time.After(time.Duration(waitTime)):
				continue
			}
		}

		return resp, nil
	}

	return nil, ErrNetworkFailed
}
