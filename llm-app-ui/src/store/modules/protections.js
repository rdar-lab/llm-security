export default {
    namespaced: true,
    state: {
        protectors: {
            'none': 'No protection',
            'llm': 'LLM Filter',
            'wrap': 'Encoded query',
            'repeat': 'Repeat instruction',
            'erase-and-check-suffix': 'Erase-and-check - Suffix',
            'erase-and-check-infusion': 'Erase-and-check - Infusion',
            'erase-and-check-insertion': 'Erase-and-check - Insertion',
        },
        selectedProtector: 'none'
    },
    mutations: {
        setSelectedProtector(state, { selectedProtector }) {
            state.selectedProtector = selectedProtector;
        },
    },
    getters: {
        selectedProtector: state => state.selectedProtector,
        getProtectors: state => state.protectors,
    }
}