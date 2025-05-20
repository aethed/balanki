(() => {
  // { [key: "again" | "hard" | "good" | "easy" | "break"]: string[] }
  const images = {}

  let feedbackTimeout = null
  let waitingForStartImages = false

  function randomImageURL (array) {
    if (typeof array === 'undefined' || array.length === 0) return null
    return array[Math.floor(Math.random() * array.length)]
  }

  // Wait for pycmd to initialize
  function retrieveImages () {
    if (typeof pycmd === 'undefined') {
      setTimeout(retrieveImages, 10)
      return
    }
    for (const type of ['again', 'hard', 'good', 'easy', 'break']) {
      window.pycmd('audiovisualFeedback#files#images/' + type, (msg) => { images[type] = JSON.parse(msg) })
    }
    window.pycmd('audiovisualFeedback#files#images/start', (msg) => {
      images.start = JSON.parse(msg)
      if (waitingForStartImages) window.avfReviewStart()
    })
  }

  function onLoad () {
    const visualFeedback = document.createElement('div')
    visualFeedback.id = 'visualFeedback'
    document.body.appendChild(visualFeedback)

    const intermission = document.createElement('div')
    intermission.id = 'avf-intermission'
    document.body.appendChild(intermission)
  }

  function showImage (array) {
    const card = document.getElementById('qa')
    const container = document.getElementById('visualFeedback')
    if (feedbackTimeout) {
      clearTimeout(feedbackTimeout)
    }

    const imgUrl = randomImageURL(array)
    if (imgUrl === null) return

    window.pycmd('audiovisualFeedback#disableShowAnswer')

    const img = document.createElement('img')
    img.src = imgUrl
    container.appendChild(img)
    container.classList.add('visible')
    card.classList.add('hidden')

    feedbackTimeout = setTimeout(() => {
      container.classList.remove('visible')
      card.classList.remove('hidden')
      container.removeChild(img)
      window.pycmd('audiovisualFeedback#enableShowAnswer')
    }, 1000)
  }

  function showIntermission(ease) {
    const card = document.getElementById('qa')
    const container = document.getElementById('avf-intermission')
    if (feedbackTimeout) {
      clearTimeout(feedbackTimeout)
    }

    const imgUrl = randomImageURL(images.break)
    if (imgUrl === null) return

    window.pycmd('audiovisualFeedback#disableShowAnswer')

    container.innerHTML = `
      <h1>Intermission</h1>
      <button>Resume Now</button>
      <img src="${imgUrl}" onclick='pycmd("audiovisualFeedback#replayIntermissionSound")'>
      <p>(Click Image To Replay)</p>
    `;
    container.querySelector("button").addEventListener('click', () => {
      container.classList.remove('visible')
      card.classList.remove('hidden')
      container.innerHTML = ''
      window.pycmd(`audiovisualFeedback#resumeReview#${ease}`)
    });

    container.classList.add('visible')
    card.classList.add('hidden')
  }

  window.avfAnswer = (ease) => {
    showImage(images[ease])
  }

  window.avfReviewStart = () => {
    if ('start' in images) {
      showImage(images.start)
    } else {
      waitingForStartImages = true
    }
  }

  window.avfIntermission = (ease) => {
    if ('break' in images) {
      showIntermission(ease)
    } else {
      waitingForStartImages = true
    }
  }

  document.readyState === 'complete' ? onLoad() : window.addEventListener('load', onLoad)
  retrieveImages()
})()
