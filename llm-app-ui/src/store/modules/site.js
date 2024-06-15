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
                if (mode === "rag") {
                    url = '/api/site_info/ask-with-rag/';
                } else if (mode === "retriever") {
                    url = '/api/site_info/ask-with-retriever/';
                } else if (mode === "retriever-embedding") {
                    url = '/api/site_info/ask-with-retriever/';
                } else {
                    reject(new Error(`Invalid mode: ${mode}`));
                    return;
                }

                url += '?site_url=' + encodeURIComponent(siteUrl);
                url += '&question=' + encodeURIComponent(query);

                if (mode === "retriever-embedding") {
                    url += '&use_embeddings=true';
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