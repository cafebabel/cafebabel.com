const container = document.querySelector('.tag-header')
const bgImg = document.querySelector('.tag-header img')

addBackgroundImage(container, bgImg)
parallax()

function parallax() {
  const container = document.querySelector('.tag-header.image')
  if (!container) return
  window.addEventListener('scroll', () => {
    const scrolledHeight = window.pageYOffset
    container.style.backgroundPositionY = `${50 + 0.05 * scrolledHeight}%`
  })
}

function addBackgroundImage(container, bgImg) {
  if (!bgImg) return
  bgImg.classList.add('hidden')
  container.style.backgroundImage = `url(${bgImg.src})`
}
