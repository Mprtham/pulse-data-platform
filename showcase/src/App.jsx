import Hero from './sections/Hero.jsx';
import WhyWhoWhich from './sections/WhyWhoWhich.jsx';
import DemoSection from './sections/DemoSection.jsx';
import WhatItDoes from './sections/WhatItDoes.jsx';
import KPIs from './sections/KPIs.jsx';
import Architecture from './sections/Architecture.jsx';
import StackChips from './sections/StackChips.jsx';
import DataQuality from './sections/DataQuality.jsx';
import WhatItProves from './sections/WhatItProves.jsx';
import FooterSection from './sections/FooterSection.jsx';

export default function App() {
  return (
    <>
      <Hero />
      <WhyWhoWhich />
      <DemoSection />
      <WhatItDoes />
      <KPIs />
      <Architecture />
      <StackChips />
      <DataQuality />
      <WhatItProves />
      <FooterSection />
    </>
  );
}
