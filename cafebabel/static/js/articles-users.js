const awesomplete = new Awesomplete('input[data-multiple]', {
  filter(text, input) {
    return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0])
  },

  item(text, input) {
    return Awesomplete.ITEM(text, input.match(/[^,]*$/)[0])
  },

  replace(text) {
    const before = this.input.value.match(/^.+,\s*|/)[0]
    this.input.value = before + text + ', '
  },

  data(text, input) {
    return { label: text.name, value: text.pk }
  }
})

window.addEventListener('load', () => {
  document.querySelector('#authors').addEventListener('keyup', event => {
    event.preventDefault()
    /* Intercept -return- it's capture by 'click' for adding tags */
    if (event.keyCode == 38) return
    let submission = event.target.value
    submission = submission.split(',').pop()
    if (submission.length < 3) return
    request(`/en/profile/suggest/?terms=${submission}`)
      .catch(console.error.bind(console))
      .then(users => {
        if (!users) awesomplete.destroy()
        awesomplete.list = users
      })
  })
})
