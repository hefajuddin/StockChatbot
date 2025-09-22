
// import React from "react";

// export default function ChatBox({ messages }) {
//   return (
//     <div
//       style={{
//         height: "400px",
//         overflowY: "auto",
//         border: "1px solid #ccc",
//         padding: "1rem",
//         borderRadius: "0.5rem",
//       }}
//     >
//       {messages.map((msg, idx) => (
//         <div
//           key={idx}
//           style={{ marginBottom: "1rem", textAlign: msg.sender === "bot" ? "left" : "right" }}
//         >
//           <strong>{msg.sender === "bot" ? "OMS Agent" : "You"}:</strong>
//           <div style={{ marginTop: "0.5rem" }}>
//             {msg.sender === "bot" && msg.recommendResponse && (
//               <div>
//                 {msg.recommendResponse.map((r, i) => (
//                   <div key={i}>{r}</div>
//                 ))}
//               </div>
//             )}

//             {msg.sender === "bot" && msg.priceResponse && msg.priceList && (
//               <div>
//                 {msg.priceResponse.map((r, i) => (
//                   <div key={i}>
//                     {r}
//                     {msg.priceList[i] && (
//                       <div style={{ marginLeft: "1rem", marginTop: "0.25rem" }}>
//                         {Object.keys(msg.priceList[i]).map((key) => {
//                           // buySellDetails আলাদা হ্যান্ডল করা
//                           if (key === "buySellDetails") {
//                             return (
//                               <table
//                                 key={i}
//                                 style={{ borderCollapse: "collapse", width: "100%", marginTop: "0.5rem" }}
//                               >
//                                 <thead>
//                                   <tr>
//                                     <th style={{ background: "#d4edda", padding: "4px" }}>Buy Price</th>
//                                     <th style={{ background: "#d4edda", padding: "4px" }}>Buy Volume</th>
//                                     <th style={{ background: "#d4edda", padding: "4px" }}>Buyer Count</th>
//                                     <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Price</th>
//                                     <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Volume</th>
//                                     <th style={{ background: "#f8d7da", padding: "4px" }}>Seller Count</th>
//                                   </tr>
//                                 </thead>
//                                 <tbody>
//                                   {msg.priceList[i][key].map((item, idx2) => (
//                                     <tr key={idx2}>
//                                       <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyPrice}</td>
//                                       <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyVolume}</td>
//                                       <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyerCount}</td>
//                                       <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellPrice}</td>
//                                       <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellVolume}</td>
//                                       <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellerCount}</td>
//                                     </tr>
//                                   ))}
//                                 </tbody>
//                               </table>
//                             );
//                           }

//                           // সাধারণ প্রাইস ইনফরমেশন
//                           return (
//                             <div key={key}>
//                               {key.toUpperCase()}: {msg.priceList[i][key]}
//                             </div>
//                           );
//                         })}
//                       </div>
//                     )}
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }







// import React from "react";

// export default function ChatBox({ messages }) {
//   return (
//     <div
//       style={{
//         height: "400px",
//         overflowY: "auto",
//         border: "1px solid #ccc",
//         padding: "1rem",
//         borderRadius: "0.5rem",
//       }}
//     >
//       {messages.map((msg, idx) => (
//         <div
//           key={idx}
//           style={{
//             marginBottom: "1rem",
//             textAlign: msg.sender === "bot" ? "left" : "right",
//           }}
//         >
//           <strong>{msg.sender === "bot" ? "OMS Agent" : "You"}:</strong>
//           <div style={{ marginTop: "0.5rem" }}>
//             {/* recommendResponse */}
//             {msg.sender === "bot" && msg.recommendResponse && (
//               <div style={{ marginBottom: "0.5rem" }}>
//                 {msg.recommendResponse.map((r, i) => (
//                   <div key={i}>{r}</div>
//                 ))}
//               </div>
//             )}

//             {/* priceResponse */}
//             {msg.sender === "bot" && msg.priceResponse && msg.priceList && (
//               <div>
//                 {msg.priceResponse.map((r, i) => {
//                   const priceItem = msg.priceList[i];

//                   // যদি buySellDetails থাকে
//                   if (priceItem.buySellDetails) {
//                     return (
//                       <div key={i} style={{ marginTop: "0.5rem" }}>
//                         {r}
//                         <table
//                           style={{
//                             borderCollapse: "collapse",
//                             width: "100%",
//                             marginTop: "0.5rem",
//                           }}
//                         >
//                           <thead>
//                             <tr>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buy Price</th>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buy Volume</th>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buyer Count</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Price</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Volume</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Seller Count</th>
//                             </tr>
//                           </thead>
//                           <tbody>
//                             {priceItem.buySellDetails.map((item, idx2) => (
//                               <tr key={idx2}>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyPrice}</td>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyVolume}</td>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyerCount}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellPrice}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellVolume}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellerCount}</td>
//                               </tr>
//                             ))}
//                           </tbody>
//                         </table>
//                       </div>
//                     );
//                   }

//                   // buySellDetails না থাকলে: প্রতিটি key-value আলাদা ব্লক
//                   return (
//                     <div
//                       key={i}
//                       style={{
//                         display: "flex",
//                         flexWrap: "wrap",
//                         gap: "0.5rem",
//                         marginTop: "0.5rem",
//                       }}
//                     >
//                       {Object.entries(priceItem).map(([key, val], idx2) => (
//                         <div
//                           key={idx2}
//                           style={{
//                             padding: "0.5rem",
//                             border: "1px solid #ccc",
//                             borderRadius: "0.5rem",
//                             backgroundColor: "#f7f7f7",
//                             minWidth: "100px",
//                             textAlign: "center",
//                           }}
//                         >
//                           <strong>{key.toUpperCase()}</strong>: {val}
//                         </div>
//                       ))}
//                     </div>
//                   );
//                 })}
//               </div>
//             )}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }






// import React from "react";

// export default function ChatBox({ messages }) {
//   return (
//     <div
//       style={{
//         height: "400px",
//         overflowY: "auto",
//         border: "1px solid #ccc",
//         padding: "1rem",
//         borderRadius: "0.5rem",
//       }}
//     >
//       {messages.map((msg, idx) => (
//         <div
//           key={idx}
//           style={{
//             marginBottom: "1rem",
//             textAlign: msg.sender === "bot" ? "left" : "right",
//           }}
//         >
//           <strong>{msg.sender === "bot" ? "OMS Agent" : "You"}:</strong>
//           <div style={{ marginTop: "0.5rem" }}>
//             {/* recommendResponse */}
//             {msg.sender === "bot" && msg.recommendResponse && (
//               <div style={{ marginBottom: "0.5rem" }}>
//                 {msg.recommendResponse.map((r, i) => (
//                   <div key={i}>{r}</div>
//                 ))}
//               </div>
//             )}

//             {/* priceResponse + priceList */}
//             {msg.sender === "bot" && msg.priceResponse && msg.priceList && (
//               <div>
//                 {msg.priceResponse.map((r, i) => {
//                   const priceItem = msg.priceList[i];

//                   // প্রতিটি response এর আগে priceResponse text
//                   return (
//                     <div key={i} style={{ marginTop: "0.5rem" }}>
//                       <div style={{ fontWeight: "bold" }}>{r}</div>

//                       {/* buySellDetails আছে */}
//                       {priceItem.buySellDetails ? (
//                         <table
//                           style={{
//                             borderCollapse: "collapse",
//                             width: "100%",
//                             marginTop: "0.5rem",
//                           }}
//                         >
//                           <thead>
//                             <tr>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buy Price</th>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buy Volume</th>
//                               <th style={{ background: "#d4edda", padding: "4px" }}>Buyer Count</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Price</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Sell Volume</th>
//                               <th style={{ background: "#f8d7da", padding: "4px" }}>Seller Count</th>
//                             </tr>
//                           </thead>
//                           <tbody>
//                             {priceItem.buySellDetails.map((item, idx2) => (
//                               <tr key={idx2}>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyPrice}</td>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyVolume}</td>
//                                 <td style={{ background: "#d4edda", padding: "4px" }}>{item.buyerCount}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellPrice}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellVolume}</td>
//                                 <td style={{ background: "#f8d7da", padding: "4px" }}>{item.sellerCount}</td>
//                               </tr>
//                             ))}
//                           </tbody>
//                         </table>
//                       ) : (
//                         // buySellDetails নেই -> প্রতিটি key-value
//                         <div
//                           style={{
//                             display: "flex",
//                             flexWrap: "wrap",
//                             gap: "0.5rem",
//                             marginTop: "0.5rem",
//                           }}
//                         >
//                           {Object.entries(priceItem).map(([key, val], idx2) => (
//                             <div
//                               key={idx2}
//                               style={{
//                                 padding: "0.5rem",
//                                 border: "1px solid #ccc",
//                                 borderRadius: "0.5rem",
//                                 backgroundColor: "#f7f7f7",
//                                 minWidth: "100px",
//                                 textAlign: "center",
//                               }}
//                             >
//                               <strong>{key.toUpperCase()}</strong>: {val}
//                             </div>
//                           ))}
//                         </div>
//                       )}
//                     </div>
//                   );
//                 })}
//               </div>
//             )}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }




// import React from "react";

// export default function ChatBox({ messages }) {
//   return (
//     <div
//       style={{
//         height: "400px",
//         overflowY: "auto",
//         border: "1px solid #ccc",
//         padding: "1rem",
//         borderRadius: "0.5rem",
//       }}
//     >
//       {messages.map((msg, idx) => (
//         <div
//           key={idx}
//           style={{
//             marginBottom: "1rem",
//             textAlign: msg.sender === "bot" ? "left" : "right",
//           }}
//         >
//           <strong>{msg.sender === "bot" ? "OMS Agent" : "You"}:</strong>

//           {/* ইউজারের ইনপুট */}
//           {msg.sender === "user" && (
//             <div
//               style={{
//                 marginTop: "0.25rem",
//                 padding: "0.25rem 0.5rem",
//                 backgroundColor: "#f1f1f1",
//                 display: "inline-block",
//                 borderRadius: "0.25rem",
//               }}
//             >
//               {msg.text}
//             </div>
//           )}

//           <div style={{ marginTop: "0.5rem" }}>
//             {/* recommendResponse */}
//             {msg.sender === "bot" && msg.recommendResponse && (
//               <div style={{ marginBottom: "0.5rem" }}>
//                 {msg.recommendResponse.map((r, i) => (
//                   <div key={i}>{r}</div>
//                 ))}
//               </div>
//             )}

//             {/* priceResponse + priceList */}
//             {msg.sender === "bot" && msg.priceResponse && msg.priceList && (
//               <div>
//                 {msg.priceResponse.map((r, i) => {
//                   const priceItem = msg.priceList[i];

//                   // প্রতিটি response এর আগে priceResponse text
//                   return (
//                     <div key={i} style={{ marginTop: "0.5rem" }}>
//                       <div style={{ fontWeight: "bold" }}>{r}</div>

//                       {/* buySellDetails আছে */}
//                       {priceItem.buySellDetails ? (
//                         <table
//                           style={{
//                             borderCollapse: "collapse",
//                             width: "100%",
//                             marginTop: "0.25rem",
//                             fontSize: "0.85rem",
//                           }}
//                         >
//                           <thead>
//                             <tr>
//                               <th style={{ background: "#d4edda", padding: "2px" }}>Buy Price</th>
//                               <th style={{ background: "#d4edda", padding: "2px" }}>Buy Volume</th>
//                               <th style={{ background: "#d4edda", padding: "2px" }}>Buyer Count</th>
//                               <th style={{ background: "#f8d7da", padding: "2px" }}>Sell Price</th>
//                               <th style={{ background: "#f8d7da", padding: "2px" }}>Sell Volume</th>
//                               <th style={{ background: "#f8d7da", padding: "2px" }}>Seller Count</th>
//                             </tr>
//                           </thead>
//                           <tbody>
//                             {priceItem.buySellDetails.map((item, idx2) => (
//                               <tr key={idx2}>
//                                 <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyPrice}</td>
//                                 <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyVolume}</td>
//                                 <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyerCount}</td>
//                                 <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellPrice}</td>
//                                 <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellVolume}</td>
//                                 <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellerCount}</td>
//                               </tr>
//                             ))}
//                           </tbody>
//                         </table>
//                       ) : (
//                         // buySellDetails নেই -> প্রতিটি key-value
//                         <div
//                           style={{
//                             display: "flex",
//                             flexWrap: "wrap",
//                             gap: "0.25rem",
//                             marginTop: "0.25rem",
//                           }}
//                         >
//                           {Object.entries(priceItem).map(([key, val], idx2) => (
//                             <div
//                               key={idx2}
//                               style={{
//                                 padding: "0.25rem 0.4rem",
//                                 border: "1px solid #ccc",
//                                 borderRadius: "0.25rem",
//                                 backgroundColor: "#f7f7f7",
//                                 minWidth: "80px",
//                                 textAlign: "center",
//                                 fontSize: "0.85rem",
//                               }}
//                             >
//                               <strong>{key.toUpperCase()}</strong>: {val}
//                             </div>
//                           ))}
//                         </div>
//                       )}
//                     </div>
//                   );
//                 })}
//               </div>
//             )}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }




import React, { useEffect, useRef } from "react";

export default function ChatBox({ messages }) {
  const containerRef = useRef(null);

  // নতুন মেসেজ এলে auto-scroll
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={containerRef}
      style={{
        height: "400px",
        overflowY: "auto",
        border: "1px solid #ccc",
        padding: "1rem",
        borderRadius: "0.5rem",
      }}
    >
      {messages.map((msg, idx) => (
        <div
          key={idx}
          style={{
            marginBottom: "1rem",
            textAlign: msg.sender === "bot" ? "left" : "right",
          }}
        >
          <strong>{msg.sender === "bot" ? "OMS Agent" : "You"}:</strong>

          {/* ইউজারের ইনপুট */}
          {msg.sender === "user" && (
            <div
              style={{
                marginTop: "0.25rem",
                padding: "0.25rem 0.5rem",
                backgroundColor: "#f1f1f1",
                display: "inline-block",
                borderRadius: "0.25rem",
              }}
            >
              {msg.text}
            </div>
          )}

          <div style={{ marginTop: "0.5rem" }}>
            {/* recommendResponse */}
            {msg.sender === "bot" && msg.recommendResponse && (
              <div style={{ marginBottom: "0.5rem" }}>
                {msg.recommendResponse.map((r, i) => (
                  <div key={i}>{r}</div>
                ))}
              </div>
            )}

            {/* priceResponse + priceList */}
            {msg.sender === "bot" && msg.priceResponse && msg.priceList && (
              <div>
                {msg.priceResponse.map((r, i) => {
                  const priceItem = msg.priceList[i];

                  // প্রতিটি response এর আগে priceResponse text
                  return (
                    <div key={i} style={{ marginTop: "0.5rem" }}>
                      <div style={{ fontWeight: "bold" }}>{r}</div>

                      {/* buySellDetails আছে */}
                      {priceItem.buySellDetails ? (
                        <table
                          style={{
                            borderCollapse: "collapse",
                            width: "100%",
                            marginTop: "0.25rem",
                            fontSize: "0.85rem",
                          }}
                        >
                          <thead>
                            <tr>
                              <th style={{ background: "#d4edda", padding: "2px" }}>Buy Price</th>
                              <th style={{ background: "#d4edda", padding: "2px" }}>Buy Volume</th>
                              <th style={{ background: "#d4edda", padding: "2px" }}>Buyer Count</th>
                              <th style={{ background: "#f8d7da", padding: "2px" }}>Sell Price</th>
                              <th style={{ background: "#f8d7da", padding: "2px" }}>Sell Volume</th>
                              <th style={{ background: "#f8d7da", padding: "2px" }}>Seller Count</th>
                            </tr>
                          </thead>
                          <tbody>
                            {priceItem.buySellDetails.map((item, idx2) => (
                              <tr key={idx2}>
                                <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyPrice}</td>
                                <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyVolume}</td>
                                <td style={{ background: "#d4edda", padding: "2px" }}>{item.buyerCount}</td>
                                <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellPrice}</td>
                                <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellVolume}</td>
                                <td style={{ background: "#f8d7da", padding: "2px" }}>{item.sellerCount}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        // buySellDetails নেই -> প্রতিটি key-value
                        <div
                          style={{
                            display: "flex",
                            flexWrap: "wrap",
                            gap: "0.25rem",
                            marginTop: "0.25rem",
                          }}
                        >
                          {Object.entries(priceItem).map(([key, val], idx2) => (
                            <div
                              key={idx2}
                              style={{
                                padding: "0.25rem 0.4rem",
                                border: "1px solid #ccc",
                                borderRadius: "0.25rem",
                                backgroundColor: "#f7f7f7",
                                minWidth: "80px",
                                textAlign: "center",
                                fontSize: "0.85rem",
                              }}
                            >
                              <strong>{key.toUpperCase()}</strong>: {val}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
