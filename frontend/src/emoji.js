// The app's emoji set (design system "Chọn emoji") drawn as images, so they look the same on every phone
// instead of each OS's emoji font. Artwork: Microsoft Fluent Emoji 3D (MIT), 128 px WebP in assets/emoji/.
// Memories/jars/events still store the Unicode emoji; anything outside this set falls back to text.
import heart from '@/assets/emoji/heart.webp'
import cake from '@/assets/emoji/cake.webp'
import coffee from '@/assets/emoji/coffee.webp'
import tulip from '@/assets/emoji/tulip.webp'
import gift from '@/assets/emoji/gift.webp'
import heartEyes from '@/assets/emoji/heart-eyes.webp'
import heartsFace from '@/assets/emoji/hearts-face.webp'
import grin from '@/assets/emoji/grin.webp'
import plane from '@/assets/emoji/plane.webp'
import tree from '@/assets/emoji/tree.webp'
import camera from '@/assets/emoji/camera.webp'
import clapper from '@/assets/emoji/clapper.webp'
import custard from '@/assets/emoji/custard.webp'
import pizza from '@/assets/emoji/pizza.webp'
import gamepad from '@/assets/emoji/gamepad.webp'
import sparkles from '@/assets/emoji/sparkles.webp'

/** Picker order (same as the design system grid). */
export const EMOJIS = ['❤️', '🎂', '☕', '🌷', '🎁', '😍', '🥰', '😀', '✈️', '🌲', '📷', '🎬', '🍮', '🍕', '🎮', '✨']
const IMAGES = [heart, cake, coffee, tulip, gift, heartEyes, heartsFace, grin, plane, tree, camera, clapper, custard, pizza, gamepad, sparkles]

const bare = emoji => (emoji || '').replace(/️/g, '')
const BY_EMOJI = new Map(EMOJIS.map((e, i) => [bare(e), IMAGES[i]]))

/** Image URL for an emoji of the set, else null (show it as text). */
export const emojiImage = emoji => BY_EMOJI.get(bare(emoji)) || null
