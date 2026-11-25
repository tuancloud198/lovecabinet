// The ragged dog pet (Cún Khố Rách): a body per growth stage (no head) + a head per mood, put together by PetArt.vue.
import body1 from './body-1.svg'
import body2 from './body-2.svg'
import body3 from './body-3.svg'
import neutral from './head-neutral.svg'
import happy from './head-happy.svg'
import shy from './head-shy.svg'
import excited from './head-excited.svg'
export default {
  bodies: [body1, body2, body3],
  heads: { neutral, happy, shy, excited },
  // Where the head goes on each body, as % of the body image: x/y = top-left of the head image, w = its width
  // (height follows the head's aspect ratio), r = rotation in degrees around the head's centre.
  anchors: [{ x: 0, y: 0, w: 100, r: 0 }, { x: 0.29, y: 0, w: 99.74, r: 0 }, { x: 0.26, y: 0, w: 99.79, r: 0 }],
  // Image sizes (viewBox width/height), so PetArt can lay both out in one SVG.
  bodySizes: [[304, 316], [317, 384], [329, 434]],
  headSize: [304, 198],
}
