window.addEventListener('load', () => {
  window.tribute = new Tribute({
    values(text, cb) {
      if (text.length < 3) return
      request(`/en/profile/suggest/?terms=${text}`)
        .catch(console.error.bind(console))
        .then(users => cb(users.map(u => {return {key: u.name, value: u.pk}})))
    },
    fillAttr: 'key',
    allowSpaces: true,
    selectTemplate(item) {
      return `<a data-id=${item.original.value}>${item.original.key}</a>`;
    }
  })

  tribute.attach(document.querySelector('#authors'))
})
