
  function request (url, params) {
    params.headers = params.headers || {}
    params.headers['Content-Type'] = 'application/json'
    params.body = params.body && JSON.stringify(params.body)
    const response = {}

    return fetch(url, params)
    .then(r => {
      if (!r.ok) {
        console.error(url, r)
        throw new Error(url)
      }
      response.status = r.status
      // `r.json()` crashes if the body is empty.
      return r.text()
    })
    .then(body => {
      response.body = body && JSON.parse(body)
      return response
    })
  }
