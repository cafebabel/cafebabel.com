const tagButtonAdd = document.querySelector('.tags button.add')
const tagButtonRemove = document.querySelector('.tags button.remove')
tagButtonAdd.addEventListener('click', (event) => {
  event.preventDefault()
  const tag = event.target.previousElementSibling.value
  if (!tag) {
    return
  }
  console.log('Tag', tag)
})

