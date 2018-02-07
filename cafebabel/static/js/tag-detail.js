const container = document.querySelector('.tag-header')
const imgUrl = container.querySelector('img')

addBackgroundImage(container, imgUrl)
parallax()

function parallax() {
  const container = document.querySelector('.tag-header.image')
  if (!container) return
  window.addEventListener('scroll', () => {
    const scrolledHeight = window.pageYOffset
    container.style.backgroundPositionY = `${50 + 0.2 * scrolledHeight}%`
  })
}

function addBackgroundImage(container, imgUrl) {
  if (!imgUrl) return
  container.querySelector('img').classList.add('hidden')
  container.style.backgroundImage = `url(${imgUrl.src})`
}
