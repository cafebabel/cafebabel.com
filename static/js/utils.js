/* global fetch */
// Inspired by https://github.com/zellwk/zl-fetch
// See https://css-tricks.com/using-fetch/
function request (url, options = undefined) {
  return fetch(url, optionsHandler(options))
    .then(handleResponse)
    .catch(error => {
        const e = new Error(`${error.message} ${url}`)
        Object.assign(e, error, {url})
        throw e
      })
}

function optionsHandler (options) {
  const def = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'}
  }

  if (!options) return def

  let r = Object.assign({}, def, options)

  // Deal with body, can be either a hash or a FormData,
  // will generate a JSON string from it if in options.
  delete r.body
  if (options.body) {
    // Allow to pass an empty hash too.
    if (!(Object.getOwnPropertyNames(options.body).length === 0)) {
      r.body = JSON.stringify(options.body)
    } else if (options.body instanceof FormData) {
      r.body = JSON.stringify(Array.from(options.body.entries()))
    }
  }
  return r
}

const handlers = {
  JSONResponseHandler (response) {
    return response.json()
      .then(json => {
        if (response.ok) {
          return json
        } else {
          return Promise.reject(Object.assign({}, json, {
            status: response.status
          }))
        }
      })
  },
  textResponseHandler (response) {
    if (response.ok) {
      return response.text()
    } else {
      return Promise.reject(Object.assign({}, {
        status: response.status,
        message: response.statusText
      }))
    }
  }
}

function handleResponse (response) {
  let contentType = response.headers.get('content-type')
  if (contentType.includes('application/json')) {
    return handlers.JSONResponseHandler(response)
  } else if (contentType.includes('text/html')) {
    return handlers.textResponseHandler(response)
  } else {
    throw new Error(`
      Sorry, content-type '${contentType}' is not supported,
      only 'application/json' and 'text/html' are.
    `)
  }
}
