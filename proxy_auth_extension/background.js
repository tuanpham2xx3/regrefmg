// Proxy authentication handler for HTTP proxies
// This extension automatically handles proxy authentication requests

chrome.webRequest.onAuthRequired.addListener(
    function(details) {
        console.log("Proxy authentication required");
        
        // Get credentials from storage (set by Python script)
        return new Promise(function(resolve) {
            chrome.storage.local.get(['proxy_username', 'proxy_password'], function(items) {
                if (items.proxy_username && items.proxy_password) {
                    console.log("Using stored credentials");
                    resolve({
                        authCredentials: {
                            username: items.proxy_username,
                            password: items.proxy_password
                        }
                    });
                } else {
                    // Fallback: cancel the request
                    console.log("No credentials found, canceling");
                    resolve({cancel: true});
                }
            });
        });
    },
    {urls: ["<all_urls>"]},
    ["blocking"]
);
