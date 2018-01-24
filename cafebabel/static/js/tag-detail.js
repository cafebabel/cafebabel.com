const container = document.querySelector('.tag-header')
const imgUrl = container.getAttribute('data-image')

addBackgroundImage(container, imgUrl)
parallax()

function parallax() {
  const container = document.querySelector('.tag-header.image')
  if (!container) return
  window.addEventListener('scroll', () => {
    const scrolledHeight = window.pageYOffset
    container.style.backgroundPositionY = 50 + 0.2 * scrolledHeight + '%'
  })
}

function addBackgroundImage(container, imgUrl) {
  if (imgUrl === 'None') {
    container.classList.add('default')
  } else {
    container.classList.add('image')
    container.style.backgroundImage = `url(${imgUrl})`
  }
}
