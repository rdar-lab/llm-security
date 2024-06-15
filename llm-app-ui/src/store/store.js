import { createStore } from 'vuex'
import auth from './modules/auth'
import transactions from './modules/transactions'
import protections from './modules/protections'
import site from './modules/site'

const store = createStore({
    modules: {
        auth,
        transactions,
        protections,
        site
    }
})

export default store