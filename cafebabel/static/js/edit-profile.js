/* display picture file name after selection on profile edit https://tympanus.net/codrops/2015/09/15/styling-customizing-file-inputs-smart-way/ */
const profileFileInput = document.querySelector(
  '.profile-page.edit .file input'
)
const profileLabel = document.querySelector('.profile-page.edit .file output')
const sizeInfo = profileFileInput.parentElement.querySelector('small')

profileFileInput &&
  profileFileInput.addEventListener('change', event => {
    const image = event.target.files[0]
    const fileName = image.name
    const reader = new FileReader()
    reader.readAsDataURL(image)
    reader.addEventListener('loadend', () => {
      const maxSize = Math.round(reader.result.length / 1024) > 500
      if (!maxSize) {
        profileLabel.innerHTML = `
    <figure>
      <img src=${reader.result} alt="Preview of your profile picture">
      <figcaption>${fileName}</figcaption>
    </figure>
  `
      } else {
        sizeInfo.classList.add('oversized')
        profileFileInput.value = ''
      }
    })
  })
