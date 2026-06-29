class LLMProvider {
  async analyzeClaim(claim, evidence, apiKey, imageUrl = null) {
    if (!apiKey) {
      throw new Error("Missing Gemini API Key. Please add it in Options.");
    }

    const promptText = `
      You are TruthLens, an evidence-based fact-checking assistant.
      Analyze the following claim against the EXACT provided evidence.
      
      NEW HARD RULES:
      1. You must answer ONLY from the retrieved evidence provided below.
      2. NEVER invent sources, organizations, scientific findings, or conclusions.
      3. If a source was not explicitly retrieved in the evidence text, it MUST NEVER appear in your response.
      4. If the retrieved evidence is insufficient, empty, or unrelated to the claim, you MUST return "Insufficient evidence" and your summary MUST literally say: "No reliable evidence was found."

      Claim: ${claim}
      Evidence: ${evidence}

      Classify the claim into one of these strict categories:
      - Verified by trusted sources
      - Contradicted by trusted sources
      - Mixed evidence
      - Insufficient evidence

      Output your response as JSON matching this format:
      {
          "status": "status_string",
          "summary": "1-2 sentence summary of what actually happened, tracing back ONLY to retrieved evidence.",
          "reasoning": "Detail the alignment. Do not fabricate explanations."
      }
      Do not include markdown wrappers like \`\`\`json. Return raw JSON.
    `;

    // Construct parts array for Gemini 2.5 Flash
    let parts = [{ text: promptText }];

    // Handle image
    if (imageUrl) {
      try {
        const imageRes = await fetch(imageUrl);
        const imageBlob = await imageRes.blob();
        
        // Convert blob to base64
        const base64Data = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result.split(',')[1]);
          reader.onerror = reject;
          reader.readAsDataURL(imageBlob);
        });

        parts.unshift({
          inlineData: {
            mimeType: imageBlob.type || "image/jpeg",
            data: base64Data
          }
        });
      } catch (e) {
        console.error("Failed to fetch image for LLM:", e);
      }
    }

    const payload = {
      contents: [{ parts }]
    };

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Gemini API failed: ${response.statusText}`);
      }

      const data = await response.json();
      let text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
      text = text.trim().replace("```json", "").replace("```", "");
      
      return JSON.parse(text);
    } catch (e) {
      console.error("LLMProvider error:", e);
      return {
        status: "Insufficient evidence",
        summary: `Could not perform reasoning. Error: ${e.message}`,
        reasoning: "AI processing error occurred during analysis."
      };
    }
  }
}

window.LLMProvider = LLMProvider;
