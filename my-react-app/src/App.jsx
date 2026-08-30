import MapView from "./MapView";
import "./App.css";
import logo from "./assets/logo.png";
import payphone from "./assets/payphone.png";
import bottom from "./assets/bottom.png";
import top from "./assets/top.png";
import { useState } from "react";

function App() {
  // const [showMap, setShowMap] = useState(false);

  // if (!showMap) {
  //   return (
  //     <main className="welcome-page">
  //       <div className="top-box">
  //         <img
  //           className="top-logo"
  //           src={logo}
  //           alt="Pay(phone) it forward"
  //         />
  //       </div>

  //       <div className="welcome-content">
  //         <img
  //           className="top-image"
  //           src={top}
  //           alt="Pay(phone) it forward"
  //         />


  //         <img
  //           className="bottom-image"
  //           src={bottom}
  //           alt="Payphone"
  //         />

  //         <div className="letter-text-box-2">
  //           hello
  //         </div>

  //       </div>
  //       {/* <p>
  //         Listen to messages left at payphones across NSW and leave one for the
  //         next person.
  //       </p> */}

  //       <button
  //         className="enter-button"
  //         onClick={() => setShowMap(true)}
  //       >
  //         Find a payphone
  //       </button>
  //     <footer className="footer"><p>© Philip Howard, Samuel Rofail, Olivia Thompson 2026.</p></footer>
  //     </main>
  //   );
  // }
  return (
    <main className="page">
      <div className="top-box">
        <img className="top-logo" src={logo} alt="Website logo" />

        <header className="header">
          {/* <h1>Pay(phone) it forward</h1> */}

          <p>
            When you dial <span className="phone-number"> 02 9037 3879 (*462 1777 8011609)</span> in payphones around NSW, you will hear 
            the message left for you by the previous person. You will then have the opportunity to leave a message for the next person.
            Please remember to be respectful.
          </p>
        </header>
      </div>
      

      <div className="map-section">
        <div className="map-text-box">
          <div className="map-text-content">
            <h2>Find payphones near you</h2>
            <p>Click a payphone to view more information.</p>
          </div>

          <img
            className="map-payphone-image"
            src={payphone}
            alt="Payphone"
          />
        </div>

        <section className="map-container">
          <MapView />
        </section>
      </div>

      <footer className="footer"><p>© Philip Howard, Samuel Rofail, Olivia Thompson 2026.</p></footer>
    </main>
  );
}

export default App;

// import { useState } from 'react'
// import heroImg from './assets/hero.png'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           type="button"
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App
