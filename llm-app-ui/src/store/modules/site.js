export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        askQuestion({ dispatch, rootState }, { mode, siteUrl, query }) {
            const { username, password } = rootState.auth;
            const { selectedProtector } = rootState.protections;
            const encodedCredentials = btoa(`${username}:${password}`);
            return new Promise((resolve, reject) => {
                let url = null;
                if (mode === "react") {
                    url = '/api/site_info/ask-with-react/';
                } else if (mode === "preloaded") {
                    url = '/api/site_info/ask-with-data/';
                } else if (mode === "rag") {
                    url = '/api/site_info/ask-with-data/';
                } else {
                    reject(new Error(`Invalid mode: ${mode}`));
                    return;
                }

                url += '?site_url=' + encodeURIComponent(siteUrl);
                url += '&question=' + encodeURIComponent(query);

                if (mode === "rag") {
                    url += '&rag=true';
                } else if (mode === "preloaded") {
                    url += '&rag=false';
                }

                if (selectedProtector !== 'none') {
                    url += '&protector=' + selectedProtector;
                }

                fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Basic ${encodedCredentials}`
                    }
                })
                    .then(async response => {
                        if (!response.ok) {
                            let errorMsg = await response.text();
                            if (!errorMsg) {
                                errorMsg = `HTTP error! status: ${response.status}`
                            }
                            throw new Error(errorMsg);
                        }
                        return response;
                    })
                    .then((response) => {
                        resolve(response);
                    })
                    .catch(error => {
                        reject(error);
                    });
            });
        }
    },
    getters: {}
}