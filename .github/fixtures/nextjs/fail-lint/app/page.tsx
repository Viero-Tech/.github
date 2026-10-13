import { formatPrice } from '../lib/format-price';

export default function Home() {
  return <main>{formatPrice(1250)}</main>;
}
