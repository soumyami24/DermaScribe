import streamlit as st
import pandas as pd
import altair as alt # Keep Altair import in case we add graphs later for future use
import html # For unescaping text in report

# --- Configuration & Data ---

# Reverted structure: Questions nested under each disease for dynamic display.
# Added weights back for potential scoring/prioritization in report (optional).
# Added 'category' to questions for breakdown chart.
# EXPANDED report content.
DISEASE_INFO = {
    'Psoriasis': {
        'short_desc': 'Autoimmune disease causing thick, red, scaly skin patches.',
        'long_desc': (
            "Psoriasis is a chronic autoimmune condition that speeds up the life cycle of skin cells, "
            "causing them to build up rapidly on the surface of the skin. These extra cells form "
            "scales and red patches that are often itchy and sometimes painful."
        ),
        'family_questions': {
            'header': "Family History (Psoriasis)",
            'questions': [
                {'id': 'fam_mother_psoriasis', 'text': 'Mother diagnosed with Psoriasis?', 'weight': 5, 'category': 'Family History'},
                {'id': 'fam_father_psoriasis', 'text': 'Father diagnosed with Psoriasis?', 'weight': 5, 'category': 'Family History'},
                {'id': 'fam_sibling_psoriasis', 'text': 'Any Siblings diagnosed with Psoriasis?', 'weight': 4, 'category': 'Family History'},
                {'id': 'fam_relative_psoriasis', 'text': 'Other close relatives (grandparents, etc.) diagnosed with Psoriasis?', 'weight': 2, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_psoriatic_arthritis', 'text': 'Family history of Psoriatic Arthritis?', 'weight': 3, 'category': 'Family History'},
                {'id': 'fam_autoimmune_psoriasis', 'text': 'Family history of other Autoimmune diseases (Crohn\'s, RA)?', 'weight': 2, 'category': 'Family History'} # Renamed ID for uniqueness
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_scaly_patches_psoriasis', 'text': 'Thick, red, scaly patches (esp. elbows, knees, scalp)?', 'weight': 4, 'category': 'Observations'},
                {'id': 'sym_silvery_scales_psoriasis', 'text': 'Patches covered with silvery scales?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_dry_cracked_psoriasis', 'text': 'Dry, cracked skin that may bleed?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_itching_burning_psoriasis', 'text': 'Itching, burning, or soreness in patches?', 'weight': 2, 'category': 'Observations'},
                {'id': 'sym_dandruff_psoriasis', 'text': 'Persistent, severe dandruff?', 'weight': 2, 'category': 'Observations'},
                {'id': 'sym_nail_pitting_psoriasis', 'text': 'Pitting, discoloration, or crumbling of fingernails or toenails?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_joint_pain_psoriasis', 'text': 'Joint pain, stiffness, or swelling?', 'weight': 4, 'category': 'Observations'}
            ]
        },
        'risk_info': (
            "**Psoriasis has a strong genetic component.** ~1/3 report family history. Risk increases significantly if one (16%) or both (50%+) parents have it. Environmental triggers also play a role."
        ),
        'dynamic_risk_info': { # Map question IDs to dynamic text
            'fam_mother_psoriasis': "**Having a parent with psoriasis is a primary risk factor.**",
            'fam_father_psoriasis': "**Having a parent with psoriasis is a primary risk factor.**",
            'fam_psoriatic_arthritis': "**Psoriatic Arthritis is directly linked.** Family history increases susceptibility.",
            'sym_joint_pain_psoriasis': "**Key symptom of Psoriatic Arthritis.** Mention this to a doctor."
        },
        'report_care': (
            "**Care & Precautions:**\n"
            "* **Moisturize Frequently:** Especially after bathing, apply thick creams/ointments (petrolatum, mineral oil based) to damp skin to lock in moisture.\n"
            "* **Avoid Skin Trauma (Koebner Phenomenon):** Protect skin from scratches, cuts, bug bites, and severe sunburns, as injury can trigger new patches.\n"
            "* **Manage Stress:** High stress often precedes flare-ups. Explore relaxation techniques like deep breathing, meditation, or yoga.\n"
            "* **Gentle Bathing:** Use lukewarm water and limit bath time. Avoid harsh scrubbing. Pat skin dry gently.\n"
            "* **Consider Climate:** Cold, dry weather often worsens psoriasis. Using a humidifier indoors can help."
        ),
        'report_use': (
            "**Helpful OTC Ingredients:**\n"
            "* **Salicylic Acid:** Helps lift and soften scales, allowing other treatments to penetrate better. Available in creams, lotions, shampoos.\n"
            "* **Coal Tar:** Reduces scaling, itching, and inflammation. Slows rapid skin cell growth. Available in various forms (shampoo, ointment); can stain and has an odor.\n"
            "* **Keratolytics (Urea, Lactic Acid):** Help exfoliate dead skin cells and moisturize.\n"
            "* **Emollients/Occlusives:** Thick, bland moisturizers (CeraVe, Cetaphil, Eucerin Psoriasis Relief, Aquaphor) are crucial for barrier support.\n"
            "* **Hydrocortisone (Low Strength):** Can temporarily relieve itching and inflammation on small areas (not for widespread use without doctor's advice)."
        ),
        'report_avoid': (
            "**Potential Triggers & Things to Avoid:**\n"
            "* **Fragrances & Dyes:** Common irritants in soaps, lotions, detergents.\n"
            "* **Alcohol-Based Products:** Can be excessively drying.\n"
            "* **Harsh Detergents (Sulfates):** Can strip natural oils. Use gentle cleansers.\n"
            "* **Certain Medications:** Beta-blockers, lithium, antimalarials, and rapid withdrawal from systemic steroids can trigger/worsen psoriasis. Discuss all meds with your doctor.\n"
            "* **Smoking & Excessive Alcohol:** Known to worsen psoriasis.\n"
            "* **Infections:** Strep throat, in particular, can trigger guttate psoriasis."
        )
    },
    'Eczema (Atopic Dermatitis)': {
        'short_desc': 'Chronic inflammatory condition causing dry, intensely itchy skin.',
        'long_desc': (
            "Eczema, or Atopic Dermatitis, is a chronic inflammatory condition that results in dry, "
            "itchy, and inflamed skin. It's often linked to a gene mutation (Filaggrin) that "
            "weakens the skin's barrier."
        ),
        'family_questions': {
            'header': "Family History (The 'Atopic Triad')",
            'questions': [
                {'id': 'fam_mother_eczema', 'text': 'Mother diagnosed with Eczema?', 'weight': 5, 'category': 'Family History'},
                {'id': 'fam_father_eczema', 'text': 'Father diagnosed with Eczema?', 'weight': 5, 'category': 'Family History'},
                {'id': 'fam_sibling_eczema', 'text': 'Any Siblings diagnosed with Eczema?', 'weight': 4, 'category': 'Family History'},
                {'id': 'fam_asthma_hayfever', 'text': 'Family history of Asthma or Hay Fever?', 'weight': 3, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_food_allergies_eczema', 'text': 'Family history of Food Allergies?', 'weight': 1, 'category': 'Family History'}
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_dry_sensitive_eczema', 'text': 'Generally dry, sensitive skin?', 'weight': 2, 'category': 'Observations'},
                {'id': 'sym_intense_itching_eczema', 'text': 'Intense itching, especially at night?', 'weight': 4, 'category': 'Observations'},
                {'id': 'sym_red_inflamed_eczema', 'text': 'Red, inflamed patches?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_oozing_crusting_eczema', 'text': 'Oozing or crusting patches?', 'weight': 3, 'category': 'Observations'},
                {'id': 'hist_childhood_eczema', 'text': 'History of Eczema or "cradle cap" as an infant/child?', 'weight': 4, 'category': 'Personal History'},
                {'id': 'sym_sweat_itching_eczema', 'text': 'Skin becomes very itchy when sweating?', 'weight': 2, 'category': 'Observations'},
                {'id': 'hist_asthma_hayfever_pers', 'text': 'Personal diagnosis of Asthma or Hay Fever?', 'weight': 3, 'category': 'Personal History'}, # Renamed ID
                {'id': 'hist_food_env_allergies_pers', 'text': 'Known personal Food or Environmental Allergies?', 'weight': 1, 'category': 'Personal History'} # Renamed ID
            ]
        },
        'risk_info': (
            "**Eczema strongly runs in families** (70-80% heritability), often linked to asthma/hay fever (atopic triad). Filaggrin (FLG) gene mutations impairing the skin barrier are common."
        ),
        'dynamic_risk_info': {
            'fam_mother_eczema': "**Strong risk factor.** The 'atopic triad' is strongly hereditary.",
            'fam_father_eczema': "**Strong risk factor.** The 'atopic triad' is strongly hereditary.",
            'hist_asthma_hayfever_pers': "**Indicates 'atopic' predisposition.** Higher likelihood of AD.",
            'hist_childhood_eczema': "**Primary indicator.** Shows lifelong susceptibility."
        },
        'report_care': (
            "**Care & Precautions:**\n"
            "* **'Soak & Seal':** Bathe/shower in lukewarm water for 5-10 min, gently pat skin partially dry, immediately apply thick moisturizer/ointment within 3 min.\n"
            "* **Identify & Avoid Triggers:** Common ones include dust mites, pollen, pet dander, sweat, stress, harsh soaps, fragrances, certain foods (work with an allergist if needed).\n"
            "* **Minimize Scratching:** Keep nails short. Use cool compresses for intense itch. Antihistamines may help at night.\n"
            "* **Choose Fabrics Carefully:** Soft cotton or bamboo are best. Avoid wool, polyester, rough seams.\n"
            "* **Use a Humidifier:** Especially in dry climates or winter."
        ),
        'report_use': (
            "**Helpful OTC Ingredients:**\n"
            "* **Ceramides:** Lipids that help restore the skin's natural barrier (e.g., CeraVe products).\n"
            "* **Hyaluronic Acid:** Humectant that draws moisture into the skin.\n"
            "* **Glycerin:** Another effective humectant.\n"
            "* **Petrolatum/Mineral Oil/Dimethicone:** Occlusives that form a protective layer to prevent water loss.\n"
            "* **Colloidal Oatmeal:** Soothes itching and inflammation (e.g., Aveeno Eczema Therapy).\n"
            "* **Niacinamide:** Can help improve barrier function and reduce inflammation."
        ),
        'report_avoid': (
            "**Potential Triggers & Things to Avoid:**\n"
            "* **Fragrance (Parfum):** Look for explicitly 'fragrance-free' products.\n"
            "* **Harsh Soaps/Cleansers (Sulfates like SLS):** Use gentle, non-soap, pH-balanced cleansers.\n"
            "* **Essential Oils:** Many are potential allergens/irritants.\n"
            "* **Chemical Sunscreen Filters (Oxybenzone, Avobenzone):** Mineral sunscreens (Zinc Oxide, Titanium Dioxide) are often better tolerated.\n"
            "* **Known Allergens:** Avoid personal food or environmental allergens.\n"
            "* **Overheating/Sweating:** Can trigger intense itching."
        )
    },
    'Melanoma (Skin Cancer)': {
        'short_desc': 'Serious skin cancer in pigment cells.',
        'long_desc': "Melanoma develops in melanocytes (pigment cells). It's dangerous due to its potential to spread if not caught early.",
        'family_questions': {
            'header': "Family History (Melanoma)",
            'questions': [
                {'id': 'fam_first_melanoma', 'text': 'First-degree relative diagnosed with Melanoma?', 'weight': 6, 'category': 'Family History'},
                {'id': 'fam_second_melanoma', 'text': 'Second-degree relative diagnosed with Melanoma?', 'weight': 3, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_unusual_moles_melanoma', 'text': 'Family history of many/unusual moles?', 'weight': 4, 'category': 'Family History'},
                {'id': 'fam_pancreatic_cancer_melanoma', 'text': 'Family history of Pancreatic Cancer?', 'weight': 3, 'category': 'Family History'},
                {'id': 'fam_gene_mutation_melanoma', 'text': 'Known family gene mutation (CDKN2A, BAP1)?', 'weight': 5, 'category': 'Family History'}
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_new_mole_melanoma', 'text': 'A new, unusual mole or spot?', 'weight': 5, 'category': 'Observations'},
                {'id': 'sym_mole_change_melanoma', 'text': 'Changes in an existing mole (ABCDEs)?', 'weight': 6, 'category': 'Observations'},
                {'id': 'sym_sore_no_heal_melanoma', 'text': 'A sore that doesn\'t heal?', 'weight': 4, 'category': 'Observations'},
                {'id': 'hist_many_moles_melanoma', 'text': 'Have more than 50 moles?', 'weight': 3, 'category': 'Personal History'},
                {'id': 'hist_atypical_moles_melanoma', 'text': 'Have any large or unusual-looking moles?', 'weight': 3, 'category': 'Personal History'},
                {'id': 'hist_sunburns_melanoma', 'text': 'History of severe, blistering sunburns?', 'weight': 3, 'category': 'Personal History'},
                {'id': 'hist_tanning_beds_melanoma', 'text': 'History of indoor tanning bed use?', 'weight': 4, 'category': 'Personal History'},
                {'id': 'hist_other_skin_cancer_melanoma', 'text': 'Personal history of other skin cancers?', 'weight': 2, 'category': 'Personal History'}
            ]
        },
        'risk_info': "**Family history is a significant risk factor (5-12% of cases).** First-degree relative increases risk ~1.7-2x.",
        'dynamic_risk_info': {
            'fam_first_melanoma': "**Very strong risk factor.** Critical for self/professional exams.",
            'fam_pancreatic_cancer_melanoma': "**Key indicator of potential genetic risk** (e.g., CDKN2A).",
            'hist_tanning_beds_melanoma': "**Major controllable risk factor.** Proven carcinogen.",
            'hist_sunburns_melanoma': "**Primary environmental risk.** Childhood burns double risk.",
            'hist_many_moles_melanoma': "**Significant risk factor.** More 'opportunities' for change."
        },
        'report_care': (
            "**Care & Precautions (CRITICAL):**\n"
            "* **Sun Protection:** Daily broad-spectrum SPF 30+, UPF clothing, hats, sunglasses, seek shade (10am-4pm).\n"
            "* **NO Tanning Beds:** Ever. They are Class 1 carcinogens.\n"
            "* **Monthly Self-Exams:** Learn the ABCDEs of melanoma. Check *everywhere*, use mirrors. Note any changes.\n"
            "* **Annual Dermatologist Exam:** Essential for early detection, especially with risk factors. Get professional full-body skin checks.\n"
            "* **Be Aware of Family History:** Inform your dermatologist of any family history of melanoma or pancreatic cancer."
        ),
        'report_use': (
            "**Helpful Products:**\n"
            "* **Broad-Spectrum Sunscreen (SPF 30+):** Mineral (Zinc Oxide, Titanium Dioxide) or Chemical filters. Reapply every 2 hours outdoors.\n"
            "* **UPF Clothing/Hats:** Offer reliable, consistent protection.\n"
            "* **Antioxidant Serums (Vitamin C, E):** Applied *under* sunscreen, can provide additional protection against UV damage (not a substitute for SPF).\n"
            "* **Lip Balm with SPF:** Protects lips."
        ),
        'report_avoid': (
            "**Avoid:**\n"
            "* **Tanning Beds & Intentional Sun Tanning:** No 'safe' tan exists.\n"
            "* **Sunburns:** Each sunburn increases risk.\n"
            "* **Expired Sunscreen:** Loses effectiveness.\n"
            "* **Ignoring Changes:** Don't wait if a mole looks suspicious. See a dermatologist ASAP."
        )
    },
    'Vitiligo': {
        'short_desc': 'Autoimmune condition causing pigment loss.',
        'long_desc': "Vitiligo is autoimmune; the immune system attacks pigment cells (melanocytes), causing white patches.",
        'family_questions': {
            'header': "Family History (Vitiligo & Autoimmune)",
            'questions': [
                {'id': 'fam_vitiligo_relative', 'text': 'Close relative diagnosed with Vitiligo?', 'weight': 4, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_autoimmune_vitiligo', 'text': 'Family history of other Autoimmune diseases?', 'weight': 2, 'category': 'Family History'}
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_vitiligo_patches', 'text': 'Patchy loss of skin color (white patches)?', 'weight': 6, 'category': 'Observations'},
                {'id': 'sym_premature_whitening_vitiligo', 'text': 'Premature whitening of hair?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_mouth_color_loss_vitiligo', 'text': 'Loss of color inside mouth?', 'weight': 3, 'category': 'Observations'},
                {'id': 'hist_other_autoimmune_pers', 'text': 'Personal diagnosis of other Autoimmune conditions?', 'weight': 2, 'category': 'Personal History'} # Renamed ID
            ]
        },
        'risk_info': "**Vitiligo has a genetic component (~20% have affected relative).** Believed autoimmune.",
        'dynamic_risk_info': {
            'fam_autoimmune_vitiligo': "**Relevant factor.** Shared autoimmune predisposition.",
            'hist_other_autoimmune_pers': "**Relevant factor.** Shared autoimmune predisposition."
        },
        'report_care': (
            "**Care & Precautions:**\n"
            "* **Sun Protection:** Depigmented skin burns easily and has no natural protection. High SPF (50+), broad-spectrum, water-resistant sunscreen is essential. UPF clothing helps.\n"
            "* **Avoid Skin Trauma:** Injury can sometimes trigger new patches (Koebner phenomenon). Be gentle with skin.\n"
            "* **Manage Stress:** Can be a trigger for some individuals.\n"
            "* **Cosmetic Camouflage:** High-coverage makeup or self-tanners (DHA) can effectively even skin tone if desired."
        ),
        'report_use': (
            "**Helpful Products:**\n"
            "* **High SPF Mineral Sunscreen:** Zinc Oxide/Titanium Dioxide are often well-tolerated.\n"
            "* **Gentle Cleansers & Moisturizers:** Avoid irritating ingredients.\n"
            "* **Self-Tanners (DHA based):** Safely stains the top layer of skin to help blend patches.\n"
            "* **Cover-up Makeup:** Brands like Dermablend offer high-coverage options."
        ),
        'report_avoid': (
            "**Potential Triggers & Things to Avoid:**\n"
            "* **Sunburn:** Can worsen vitiligo and increases skin cancer risk on depigmented skin.\n"
            "* **Harsh Chemicals:** Some report sensitivity to phenols (e.g., in some hair dyes, industrial chemicals).\n"
            "* **Excessive Skin Friction/Trauma:** Due to Koebner phenomenon risk."
        )
    },
    # --- Other diseases need similar expansion of care/use/avoid ---
    'Ichthyosis Vulgaris': {
        'short_desc': 'Inherited dry, \'fish-scale\' skin.',
        'long_desc': 'Common inherited disorder; skin cells don\'t shed properly. Linked to Filaggrin (FLG) gene.',
        'family_questions': {
            'header': "Family History",
            'questions': [
                {'id': 'fam_iv_parent', 'text': 'Parent diagnosed with Ichthyosis Vulgaris or has very dry, "fish-scale" skin?', 'weight': 6, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_eczema_iv_link', 'text': 'Strong family history of Eczema?', 'weight': 2, 'category': 'Family History'}
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_fish_scales_iv', 'text': 'Persistent dry, thickened, "fish-scale" like skin?', 'weight': 5, 'category': 'Observations'},
                {'id': 'sym_scales_small_iv', 'text': 'Scales are small, white, or gray?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_itching_mild_iv', 'text': 'Itching is usually mild?', 'weight': 1, 'category': 'Observations'},
                {'id': 'sym_worse_cold_iv', 'text': 'Symptoms worse in cold, dry weather?', 'weight': 2, 'category': 'Observations'},
                {'id': 'hist_eczema_iv_link', 'text': 'Do you also have Eczema (Atopic Dermatitis)?', 'weight': 3, 'category': 'Personal History'}
            ]
        },
        'risk_info': "**Common inherited disorder (often Autosomal Dominant).** Linked to FLG gene.",
        'dynamic_risk_info': {
            'hist_eczema_iv_link': "**Common co-condition.** Both linked to FLG mutations."
        },
        'report_care': '**Care:** Frequent moisturizing (esp. after bathing on damp skin), lukewarm baths (add bath oil), use a humidifier, gentle exfoliation (if recommended by doctor).',
        'report_use': '**Help:** Moisturizers with Urea, Lactic Acid, or Salicylic Acid (keratolytics); thick ointments (petrolatum); ammonium lactate lotion (prescription or OTC).',
        'report_avoid': '**Avoid:** Hot/long baths/showers, harsh soaps, low humidity, scrubbing skin vigorously.'
    },
    'Neurofibromatosis Type 1 (NF1)': {
        'short_desc': 'Genetic disorder: light-brown spots, nerve tumors.',
        'long_desc': 'NF1 causes café-au-lait spots and benign nerve tumors (neurofibromas).',
        'family_questions': {
            'header': "Family History",
            'questions': [
                {'id': 'fam_nf1_parent', 'text': 'Parent diagnosed with NF1?', 'weight': 6, 'category': 'Family History'}
            ],
            'linked_conditions': []
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_cafe_au_lait_nf1', 'text': 'Six or more light-brown flat spots?', 'weight': 6, 'category': 'Observations'},
                {'id': 'sym_axillary_freckling_nf1', 'text': 'Freckling in armpits or groin?', 'weight': 5, 'category': 'Observations'},
                {'id': 'sym_nf1_bumps', 'text': 'Soft, pea-sized bumps on/under skin?', 'weight': 5, 'category': 'Observations'},
                {'id': 'sym_lisch_nodules_nf1', 'text': 'Tiny bumps on iris (seen by eye doctor)?', 'weight': 4, 'category': 'Observations'}
            ]
        },
        'risk_info': "**Autosomal Dominant.** 50% inherited, 50% spontaneous.",
        'dynamic_risk_info': {
            'sym_cafe_au_lait_nf1': "**Primary diagnostic criterion.** Warrants specialist evaluation."
        },
        'report_care': '**Care:** Requires regular monitoring by specialists (neurology, dermatology, ophthalmology, oncology). Skin care is secondary; gentle cleansing, moisturising, sun protection.',
        'report_use': '**Help:** Gentle, fragrance-free products. Sunscreen.',
        'report_avoid': '**Avoid:** Trauma to neurofibromas. Focus on overall medical management.'
    },
    'Hidradenitis Suppurativa (HS)': {
        'short_desc': 'Painful lumps/tracts in skin folds.',
        'long_desc': 'HS causes recurring boil-like lumps, tunnels, and scarring in areas like armpits/groin.',
        'family_questions': {
            'header': "Family History",
            'questions': [
                {'id': 'fam_hs_relative', 'text': 'Close relative diagnosed with HS?', 'weight': 5, 'category': 'Family History'}
            ],
            'linked_conditions': []
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_hs_lumps', 'text': 'Painful, recurring lumps/abscesses in skin folds?', 'weight': 5, 'category': 'Observations'},
                {'id': 'sym_hs_tunnels', 'text': 'Tunnels (sinus tracts) under skin?', 'weight': 4, 'category': 'Observations'},
                {'id': 'sym_hs_scars', 'text': 'Pitted, rope-like scars in affected areas?', 'weight': 3, 'category': 'Observations'},
                {'id': 'hist_smoking_hs', 'text': 'Current or former smoker?', 'weight': 4, 'category': 'Personal History'},
                {'id': 'hist_overweight_hs', 'text': 'Significantly overweight?', 'weight': 3, 'category': 'Personal History'}
            ]
        },
        'risk_info': "**Significant family link (30-40%).** Smoking/obesity are major triggers.",
        'dynamic_risk_info': {
            'hist_smoking_hs': "**Strongest known trigger.** Quitting is critical.",
            'hist_overweight_hs': "**Major risk factor.** Increases friction/inflammation."
        },
        'report_care': '**Care:** Wear loose clothing, maintain healthy weight, **quit smoking**, gentle cleansing (avoid scrubbing), warm compresses on flares, manage stress.',
        'report_use': '**Help:** Antiseptic washes (chlorhexidine, benzoyl peroxide), gentle non-comedogenic moisturizers. (Topical/oral antibiotics & biologics require prescription).',
        'report_avoid': '**Avoid:** Tight clothing/friction, smoking, dairy (for some), high glycemic index foods (potential triggers for some), harsh deodorants/antiperspirants in affected areas.'
    },
    'Rosacea': {
        'short_desc': 'Facial redness, flushing, bumps.',
        'long_desc': 'Rosacea causes facial redness, visible blood vessels, and sometimes acne-like bumps.',
        'family_questions': {
            'header': "Family History",
            'questions': [
                {'id': 'fam_rosacea_relative', 'text': 'Close relative with Rosacea/significant facial redness?', 'weight': 4, 'category': 'Family History'}
            ],
            'linked_conditions': [
                {'id': 'fam_ancestry_rosacea', 'text': 'Family history of Northern European (Celtic) ancestry?', 'weight': 1, 'category': 'Family History'}
            ]
        },
        'symptom_questions': {
            'header': "Personal History & Observations",
            'questions': [
                {'id': 'sym_flushing_rosacea', 'text': 'Frequent blushing/flushing (center face)?', 'weight': 4, 'category': 'Observations'},
                {'id': 'sym_facial_redness_rosacea', 'text': 'Persistent facial redness?', 'weight': 4, 'category': 'Observations'},
                {'id': 'sym_broken_vessels_rosacea', 'text': 'Visible broken blood vessels on face?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_rosacea_bumps', 'text': 'Small, red, pus-filled bumps on face?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_sting_burn_rosacea', 'text': 'Skin stings/burns with products?', 'weight': 3, 'category': 'Observations'},
                {'id': 'sym_triggers_rosacea', 'text': 'Flushing after spicy food or alcohol?', 'weight': 2, 'category': 'Observations'}
            ]
        },
        'risk_info': "**Strongly runs in families,** esp. fair skin.",
        'dynamic_risk_info': {
            'sym_sting_burn_rosacea': "**Indicates compromised barrier.** Requires gentle products.",
            'sym_triggers_rosacea': "**Classic triggers.** Avoidance is key."
        },
        'report_care': '**Care:** Identify & avoid personal triggers (sun, heat, alcohol, spicy food, stress, certain products), daily broad-spectrum SPF, very gentle cleansing/handling, use lukewarm water.',
        'report_use': '**Help:** Mineral sunscreen (Zinc/Titanium), gentle non-soap cleansers, barrier-repairing moisturizers (ceramides, niacinamide), Azelaic acid (OTC reduces redness/bumps), Sulphur washes/creams.',
        'report_avoid': '**Avoid:** Physical scrubs, harsh exfoliants (high AHA/BHA), alcohol-based toners, witch hazel, fragrance, menthol, camphor, essential oils. Known triggers.'
    },
    'Epidermolysis Bullosa (EB)': {
        'short_desc': 'Extremely fragile, blistering skin.',
        'long_desc': 'Rare genetic diseases causing skin fragility; minor friction leads to blisters.',
        'family_questions': {'header': "Family History", 'questions': [{'id': 'fam_eb_hist', 'text': 'Known family history of EB?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id': 'sym_fragile_blistering_eb', 'text': 'Extremely fragile skin, blisters easily?', 'weight': 6, 'category': 'Observations'}, {'id': 'sym_mouth_blisters_eb', 'text':'Blisters inside mouth/throat?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_nail_loss_eb', 'text':'Nail deformities or loss?', 'weight': 3, 'category': 'Observations'}]},
        'risk_info': 'Rare inherited connective tissue diseases.',
        'dynamic_risk_info': {'sym_fragile_blistering_eb': "**Defining characteristic.** Requires immediate medical evaluation."},
        'report_care': '**Care:** Highly specialized medical care is essential. Focus on meticulous wound care, pain management, nutritional support, and preventing friction/trauma.',
        'report_use': '**Help:** Only use products recommended by EB specialists. Special non-adherent dressings, protective padding, specific emollients.',
        'report_avoid': '**Avoid:** Friction, rubbing, harsh soaps, adhesives, rough clothing/bedding. Requires professional medical guidance.'
    },
    'Tuberous Sclerosis (TSC)': {
        'short_desc': 'Benign tumors in brain/organs.',
        'long_desc': 'TSC causes benign tumors; skin signs (ash-leaf spots, facial angiofibromas) often appear first.',
        'family_questions': {'header': "Family History", 'questions': [{'id': 'fam_tsc_parent', 'text':'Parent diagnosed with TSC?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id': 'sym_ash_leaf_tsc', 'text':'Patches of light-colored skin?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_tsc_face_bumps', 'text':'Reddish, acne-like bumps on face?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_shagreen_tsc', 'text':'Thickened skin patches?', 'weight': 4, 'category': 'Observations'}]},
        'risk_info': 'Autosomal Dominant (~1/3 inherited).',
        'dynamic_risk_info': {'sym_ash_leaf_tsc': "**Often earliest sign.** Warrants medical evaluation."},
        'report_care': '**Care:** Requires comprehensive medical management across specialties. Skin care involves sun protection (light spots are more sensitive), gentle cleansing. Facial lesions may be treated by a dermatologist (laser, topical mTOR inhibitors).',
        'report_use': '**Help:** Gentle cleansers, broad-spectrum sunscreen.',
        'report_avoid': '**Avoid:** Sun exposure on hypopigmented spots without protection. This is primarily managed medically.'
    },
    'Hailey-Hailey Disease (Benign Familial Pemphigus)': {
        'short_desc': 'Blisters/rashes in skin folds.',
        'long_desc': 'Rare inherited disorder causing blisters in folds, triggered by heat/sweat/friction.',
        'family_questions': {'header': "Family History", 'questions': [{'id': 'fam_hailey_relative', 'text':'Close relative with Hailey-Hailey?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_fold_blisters_hailey', 'text':'Painful blisters/rashes in skin folds?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_triggers_hailey', 'text':'Triggered by heat, sweat, friction?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_cobble_hailey', 'text':'Skin appears cobblestoned/cracked?', 'weight': 3, 'category': 'Observations'}]},
        'risk_info': 'Rare Autosomal Dominant (ATP2C1 gene).',
        'dynamic_risk_info': {'sym_triggers_hailey': "**Classic presentation.** Management involves minimizing triggers."},
        'report_care': '**Care:** Keep skin folds cool & dry, wear loose/soft clothing, gentle cleansing, manage sweat (antiperspirants if tolerated), prevent secondary infection.',
        'report_use': '**Help:** Antimicrobial washes (chlorhexidine), barrier creams (zinc oxide), absorbent powders (cornstarch-based, avoid talc).',
        'report_avoid': '**Avoid:** Heat, humidity, sweating, friction/rubbing, tight clothing, occlusive ointments in folds.'
    },
    'Darier Disease (Keratosis Follicularis)': {
        'short_desc': 'Greasy, warty bumps (scalp, chest).',
        'long_desc': 'Inherited disorder with greasy bumps, often on scalp/chest/back; nail changes common.',
        'family_questions': {'header': "Family History", 'questions': [{'id':'fam_darier_parent', 'text':'Parent with Darier Disease?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_darier_bumps', 'text':'Greasy, warty bumps (scalp/chest/back)?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_nail_darier', 'text':'Nail changes (streaks/nicks)?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_sun_worsen_darier', 'text':'Worsens with sun exposure?', 'weight': 4, 'category': 'Observations'}]},
        'risk_info': 'Autosomal Dominant (ATP2A2 gene).',
        'dynamic_risk_info': {'sym_sun_worsen_darier': "**Major trigger.** Sun protection critical."},
        'report_care': '**Care:** Strict sun avoidance/protection (sunscreen, clothing), keep skin cool, gentle cleansing, avoid friction.',
        'report_use': '**Help:** Broad-spectrum sunscreen, gentle cleansers, moisturizers. Dermatologist may prescribe topical retinoids, keratolytics (lactic acid), or antibiotics if infected.',
        'report_avoid': '**Avoid:** Sun exposure, heat, sweating, friction, occlusive clothing.'
    },
    'Ehlers-Danlos Syndrome (EDS)': {
        'short_desc': 'Stretchy skin, hypermobile joints.',
        'long_desc': 'Inherited connective tissue disorders affecting collagen; classical type has stretchy, fragile skin.',
        'family_questions': {'header': "Family History", 'questions': [{'id':'fam_eds_hist', 'text':'Family history of EDS/hypermobility/unusual scarring?', 'weight': 5, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_stretchy_skin_eds', 'text':'Very soft, velvety, stretchy skin?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_fragile_skin_eds', 'text':'Fragile skin (tears/bruises easily)?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_poor_healing_eds', 'text':'Slow/poor wound healing, wide scars?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_hypermobility_eds', 'text':'Joint hypermobility?', 'weight': 5, 'category': 'Observations'}]},
        'risk_info': 'Group of inherited disorders (mostly Autosomal Dominant).',
        'dynamic_risk_info': {'sym_hypermobility_eds': "**Core feature.** Faulty collagen affects joints too."},
        'report_care': '**Care:** Protect skin from trauma (padding, careful activity choices), specialized wound care (steri-strips, careful suturing), physical therapy for joint stability.',
        'report_use': '**Help:** Gentle cleansers, moisturizers, medical-grade paper/silicone tape. Vitamin C supplementation *may* help (discuss with doctor).',
        'report_avoid': '**Avoid:** High-impact activities, trauma, friction, standard adhesive bandages (can tear skin upon removal).'
    },
    'Pseudoxanthoma Elasticum (PXE)': {
        'short_desc': 'Affects elastic fibers (skin, eyes, vessels).',
        'long_desc': 'Rare genetic disorder; elastic fibers calcify. Skin shows yellowish bumps (neck/armpits).',
        'family_questions': {'header': "Family History", 'questions': [{'id':'fam_pxe_sibling', 'text':'Sibling diagnosed with PXE?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_pxe_bumps', 'text':'Small, yellowish bumps (neck/armpits)?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_skin_plucked_pxe', 'text':'Skin loose/wrinkled like plucked chicken?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_vision_pxe', 'text':'Changes in vision?', 'weight': 5, 'category': 'Personal History'}]}, # Changed category
        'risk_info': 'Autosomal Recessive (ABCC6 gene).',
        'dynamic_risk_info': {'sym_vision_pxe': "**Critical symptom.** Requires ophthalmologist eval."},
        'report_care': '**Care:** Multi-specialist care (dermatology, ophthalmology, cardiology). Regular eye exams crucial. Avoid contact sports. Discuss calcium/aspirin use with doctor.',
        'report_use': '**Help:** Gentle skincare routines. Focus is on managing systemic effects.',
        'report_avoid': '**Avoid:** Contact sports, head trauma, potentially high-dose calcium supplements, NSAIDs/aspirin unless medically necessary.'
    },
    'Xeroderma Pigmentosum (XP)': {
        'short_desc': 'Impaired UV DNA repair, high cancer risk.',
        'long_desc': 'Rare inherited disorder impairing UV DNA repair; extreme sun sensitivity, high cancer risk.',
        'family_questions': {'header': "Family History", 'questions': [{'id':'fam_xp_sibling', 'text':'Sibling diagnosed with XP?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_severe_sunburn_xp', 'text':'Severe sunburn after minimal sun?', 'weight': 6, 'category': 'Observations'}, {'id':'sym_freckles_early_xp', 'text':'Many freckles at early age?', 'weight': 4, 'category': 'Observations'}, {'id':'sym_dry_thin_xp', 'text':'Very dry, thin skin?', 'weight': 3, 'category': 'Observations'}]},
        'risk_info': 'Rare Autosomal Recessive.',
        'dynamic_risk_info': {'sym_severe_sunburn_xp': "**Hallmark symptom.** Major red flag."},
        'report_care': '**Care (Life-Saving):** Total UV avoidance (daylight indoors, UV-blocking films, protective gear), frequent dermatologist checks for skin cancer, ophthalmology checks.',
        'report_use': '**Help:** Highest SPF broad-spectrum sunscreen (applied constantly when unavoidable exposure occurs), specialized UV-protective clothing/face shields/glasses.',
        'report_avoid': '**Avoid:** ALL UV light sources (sun, some artificial lights). This requires extreme lifestyle modification under medical guidance.'
    },
    'Albinism (Oculocutaneous)': {
        'short_desc': 'Little/no melanin pigment.',
        'long_desc': 'Inherited disorders with little/no melanin; affects skin, hair, eyes. Extreme sun sensitivity.',
        'family_questions': {'header': "Family History", 'questions': [{'id':'fam_albinism_sibling', 'text':'Sibling diagnosed with Albinism?', 'weight': 6, 'category': 'Family History'}], 'linked_conditions': []},
        'symptom_questions': {'header': "Personal History & Observations", 'questions': [{'id':'sym_no_pigment_alb', 'text':'Little/no pigment in skin, hair, eyes?', 'weight': 6, 'category': 'Observations'}, {'id':'sym_sun_sensitive_alb', 'text':'Skin very pale and sun-sensitive?', 'weight': 5, 'category': 'Observations'}, {'id':'sym_vision_albinism', 'text':'Vision problems (eye movements, light sensitivity)?', 'weight': 6, 'category': 'Observations'}]},
        'risk_info': 'Group of Autosomal Recessive disorders.',
        'dynamic_risk_info': {'sym_vision_albinism': "**Core feature.** Lack of pigment affects eye development."},
        'report_care': '**Care:** Meticulous sun protection (high SPF, clothing, hats, sunglasses) lifelong to prevent burns/cancer. Regular eye exams with low-vision aids if needed.',
        'report_use': '**Help:** High SPF (50+) broad-spectrum mineral sunscreen, UPF clothing, wide-brim hats, UV-blocking sunglasses.',
        'report_avoid': '**Avoid:** Unprotected sun exposure. Tanning is impossible and dangerous.'
    }
}


# Get list of all disease names
ALL_DISEASE_NAMES = sorted(list(DISEASE_INFO.keys())) # Corrected reference

# --- Page Navigation Functions ---

def show_home():
    """Displays the main disclaimer and welcome page."""
    show_stepper("Home (Disclaimer)")
    # Wrap content in a card-container div
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.title("Welcome!") # Simplified Title for Home

    st.warning(
        "**IMPORTANT MEDICAL DISCLAIMER**\n\n"
        "This tool is **NOT** a substitute for professional medical advice, diagnosis, or treatment. "
        "It **CANNOT** predict or diagnose any disease.\n\n"
        "The information provided is based on general associations and is for educational purposes ONLY. "
        "**Consult a qualified dermatologist** for any health concerns."
    )
    st.markdown(
        """
        <p class="homepage-text" style="font-size: 1.1rem; color: var(--color-text-medium);">
        This tool uses a dynamic questionnaire to explore potential connections between family history, personal observations, and common genetic skin conditions for educational purposes.
        <br><br>
        Follow these steps:
        <ol>
            <li>Answer questions about conditions in your family and symptoms you've noticed.</li>
            <li>Receive an educational report highlighting potential areas for discussion with a doctor.</li>
        </ol>
        </p>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.button("Start Questionnaire →", on_click=lambda: st.session_state.update(page="Step 1: Questionnaire", diseases_to_ask=[], answers={}), type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close card-container


def show_questionnaire():
    """Single page for selecting diseases and answering questions dynamically."""
    show_stepper("Step 1: Questionnaire")

    # Wrap content in a card-container div
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.title("Step 1: Select Conditions & Fill Questionnaire")
    st.info("First, select one or more conditions you are interested in learning about. Then, answer the questions that appear below for each selection.")

    # Initialize necessary state variables
    if 'diseases_to_ask' not in st.session_state:
        st.session_state.diseases_to_ask = []
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    # --- Disease Selection (This is the dropdown you want to keep) ---
    selected_diseases = st.multiselect(
        "Select conditions of interest:",
        options=ALL_DISEASE_NAMES,
        default=st.session_state.diseases_to_ask, # Persist selection
        key="disease_selector"
    )
    st.session_state.diseases_to_ask = selected_diseases # Update state

    st.markdown("---")

    # --- Dynamic Question Sections ---
    if not selected_diseases:
        st.info("Please select at least one condition to see relevant questions.")
    else:
        st.markdown("#### Please answer the questions below:")

        for disease_name in selected_diseases:
            # Ensure a dictionary exists for this disease's answers
            if disease_name not in st.session_state.answers:
                st.session_state.answers[disease_name] = {}

            # --- ERROR CHECK: Make sure disease_name is valid before accessing ---
            if disease_name not in DISEASE_INFO:
                st.error(f"Internal error: Data for '{disease_name}' not found. Skipping.")
                continue
            # --- END ERROR CHECK ---

            disease_data = DISEASE_INFO[disease_name]

            # --- MODIFICATION: Replaced st.expander with st.container(border=True) ---
            # Add a header to replace the expander title
            st.markdown(f"#### Questionnaire for: {disease_name}") 
            with st.container(border=True): # This is the "normaal container"

                # --- Family History Section ---
                if 'family_questions' in disease_data:
                    fam_data = disease_data['family_questions']
                    st.markdown(f"**{fam_data.get('header', 'Family History')}**")

                    if 'questions' in fam_data:
                        for q_info in fam_data['questions']:
                            q_id = q_info['id']
                            q_text = q_info['text']
                            current_answer = st.session_state.answers[disease_name].get(q_id, False)
                            answer = st.checkbox(q_text, value=current_answer, key=f"{disease_name}_{q_id}")
                            st.session_state.answers[disease_name][q_id] = answer

                    if 'linked_conditions' in fam_data and fam_data['linked_conditions']:
                        st.markdown("*Related Family Conditions:*")
                        for q_info in fam_data['linked_conditions']:
                            q_id = q_info['id']
                            q_text = q_info['text']
                            current_answer = st.session_state.answers[disease_name].get(q_id, False)
                            answer = st.checkbox(q_text, value=current_answer, key=f"{disease_name}_{q_id}")
                            st.session_state.answers[disease_name][q_id] = answer
                    st.markdown("<br>", unsafe_allow_html=True) # Add space


                # --- Personal Observations Section ---
                if 'symptom_questions' in disease_data:
                    sym_data = disease_data['symptom_questions']
                    st.markdown(f"**{sym_data.get('header', 'Personal History & Observations')}**")

                    if 'questions' in sym_data:
                        for q_info in sym_data['questions']:
                            q_id = q_info['id']
                            q_text = q_info['text']
                            current_answer = st.session_state.answers[disease_name].get(q_id, False)
                            answer = st.checkbox(q_text, value=current_answer, key=f"{disease_name}_{q_id}")
                            st.session_state.answers[disease_name][q_id] = answer
            
            st.markdown("<br>", unsafe_allow_html=True) # Add space between containers
            # --- END MODIFICATION ---


    st.markdown("---") # After all disease sections

    # --- Navigation Buttons ---
    cols = st.columns(2)
    with cols[0]:
        st.button("← Back to Home", on_click=lambda: st.session_state.update(page="Home (Disclaimer)", diseases_to_ask=[], answers={}), type="secondary", use_container_width=True)
    with cols[1]:
        # Enable report generation only if at least one disease is selected
        report_button_disabled = not bool(st.session_state.diseases_to_ask)
        st.button("Generate Educational Report →", on_click=lambda: st.session_state.update(page="Step 2: Your Report"), type="primary", disabled=report_button_disabled, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True) # Close card-container

def show_analysis_report():
    """Displays the final report for each selected disease."""
    show_stepper("Step 2: Your Report")

    # Ensure selections and answers exist
    if 'diseases_to_ask' not in st.session_state or not st.session_state.diseases_to_ask:
        st.error("No conditions were selected in the questionnaire. Please go back.")
        if st.button("← Back to Questionnaire", key="err_back_q"):
            st.session_state.page = "Step 1: Questionnaire"
            st.rerun()
        st.stop()

    if 'answers' not in st.session_state:
        st.error("Questionnaire answers not found. Please fill out the questionnaire first.")
        if st.button("← Back to Questionnaire", key="err_back_q_ans"):
            st.session_state.page = "Step 1: Questionnaire"
            st.rerun()
        st.stop()


    selected_for_report = st.session_state.diseases_to_ask
    all_answers = st.session_state.answers

    # --- Prepare data and calculate scores ---
    disease_scores = {} # Store scores for reuse

    # Calculate scores first
    for disease_name in selected_for_report:
        if disease_name not in DISEASE_INFO: continue # Skip if data missing

        disease_data = DISEASE_INFO[disease_name]
        disease_answers = all_answers.get(disease_name, {})
        current_score = 0
        max_possible_score = 0

        all_qs_for_disease = []
        if 'family_questions' in disease_data:
            all_qs_for_disease.extend(disease_data['family_questions'].get('questions', []))
            all_qs_for_disease.extend(disease_data['family_questions'].get('linked_conditions', []))
        if 'symptom_questions' in disease_data:
            all_qs_for_disease.extend(disease_data['symptom_questions'].get('questions', []))

        for q_info in all_qs_for_disease:
            q_id = q_info['id']
            q_weight = q_info.get('weight', 1)
            max_possible_score += q_weight
            if disease_answers.get(q_id, False):
                current_score += q_weight

        alignment_percent = (current_score / max_possible_score * 100) if max_possible_score > 0 else 0
        disease_scores[disease_name] = {'score': current_score, 'max_score': max_possible_score, 'percent': alignment_percent}


    # Using st.container to apply potential card styling to the whole report page
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.title("Educational Report")

    st.error(
        "**Reminder:** This report shows EDUCATIONAL information based on your questionnaire answers for each selected condition. "
        "It is **NOT** a medical diagnosis, risk score, or prediction. Alignment scores reflect patterns based on general associations only. "
        "**Always consult a qualified dermatologist** for any health concerns."
    )

    if not selected_for_report:
        st.info("You did not select any conditions in the questionnaire.")
        st.stop()


    # --- Display Individual Disease Reports ---
    st.markdown("---")
    st.header("Detailed Report Sections")

    # Sort the report sections by alignment score, highest first
    sorted_report_order = sorted(selected_for_report, key=lambda d: disease_scores.get(d, {}).get('percent', 0), reverse=True)


    for disease_name in sorted_report_order: # Iterate in sorted order
        # --- ERROR CHECK: Ensure disease_name is valid before proceeding ---
        if disease_name not in DISEASE_INFO or disease_name not in disease_scores:
            st.error(f"Internal error: Data or score for '{disease_name}' not found. Cannot generate report section.")
            continue
        # --- END ERROR CHECK ---

        disease_data = DISEASE_INFO[disease_name]
        disease_answers = all_answers.get(disease_name, {}) # Get answers for this disease
        score_info = disease_scores[disease_name]
        alignment_percent = score_info['percent']

        # Define Alignment Levels (Adjust thresholds as needed)
        if alignment_percent > 60:
            alignment_level = "High"
            alignment_color = "#BC4749" # Use theme colors - darker red/pink
        elif alignment_percent >= 30:
            alignment_level = "Moderate"
            alignment_color = "#957DAD" # Use accent purple
        else:
            alignment_level = "Low"
            alignment_color = "#6D617A" # Use medium text color


        with st.expander(f"**Report Section: {disease_name}** (Alignment: {alignment_level} - {alignment_percent:.0f}%)", expanded=True):

            st.markdown(f"### Educational Alignment: <span style='color:{alignment_color};'>{alignment_level} ({alignment_percent:.0f}%)</span>", unsafe_allow_html=True)

            # --- Calculate Factor Category Breakdown ---
            family_score = 0
            personal_hist_score = 0
            observation_score = 0
            dynamic_info = disease_data.get('dynamic_risk_info', {})
            contributing_factors_raw_text = [] # Store raw text for cleanup

            all_qs_for_disease = []
            if 'family_questions' in disease_data:
                all_qs_for_disease.extend(disease_data['family_questions'].get('questions', []))
                all_qs_for_disease.extend(disease_data['family_questions'].get('linked_conditions', []))
            if 'symptom_questions' in disease_data:
                all_qs_for_disease.extend(disease_data['symptom_questions'].get('questions', []))

            for q_info in all_qs_for_disease:
                q_id = q_info['id']
                q_weight = q_info.get('weight', 1)
                q_category = q_info.get('category', 'Observations') # Default if category missing

                if disease_answers.get(q_id, False): # If user checked this box
                    # Add to category score
                    if q_category == 'Family History':
                        family_score += q_weight
                    elif q_category == 'Personal History':
                        personal_hist_score += q_weight
                    else: # Observations
                        observation_score += q_weight

                    # Store cleaned text for display
                    raw_text = q_info['text']
                    # Use html.unescape and strip '?'
                    cleaned_text = html.unescape(raw_text).strip().rstrip('?')
                    factor_display_text = f"<li>{cleaned_text}</li>" # Use list item
                    if q_id in dynamic_info:
                        # Use html.unescape for dynamic info too
                        dynamic_explanation = html.unescape(dynamic_info[q_id])
                        factor_display_text = f"<li>{cleaned_text} <i>({dynamic_explanation})</i></li>" # Add dynamic info in italics
                    contributing_factors_raw_text.append(factor_display_text)

            total_score = score_info['score']
            family_contrib = (family_score / total_score * 100) if total_score > 0 else 0
            personal_hist_contrib = (personal_hist_score / total_score * 100) if total_score > 0 else 0
            observation_contrib = (observation_score / total_score * 100) if total_score > 0 else 0


            st.markdown("#### Factors You Indicated:")
            if contributing_factors_raw_text: # Use the cleaned list
                st.markdown(f"<ul>{''.join(contributing_factors_raw_text)}</ul>", unsafe_allow_html=True) # Display as HTML list
                # Display category contribution
                st.caption(f"Breakdown: Family History Factors contributed ~{family_contrib:.0f}% | Personal History ~{personal_hist_contrib:.0f}% | Observations ~{observation_contrib:.0f}% to this alignment score.")
            else:
                st.markdown("_You did not select any specific factors listed for this condition in the questionnaire._")

            # --- ENHANCED: Educational Interpretation based on Alignment ---
            st.markdown("---")
            st.markdown("#### Educational Interpretation & Next Steps:")
            if alignment_level == "High":
                st.error( # Use error color for high alignment emphasis
                    f"**High Educational Alignment ({alignment_percent:.0f}%):** Your answers strongly align with common factors associated with **{disease_name}**. "
                    f"This **DOES NOT** mean you have this condition. However, it strongly suggests discussing the specific factors you selected (listed above) "
                    f"with a qualified dermatologist. Reviewing the 'Special Care', 'Helpful Ingredients', and 'Triggers to Avoid' tabs below provides relevant educational context for that discussion."
                )
            elif alignment_level == "Moderate":
                st.warning( # Use warning color for moderate
                    f"**Moderate Educational Alignment ({alignment_percent:.0f}%):** Your answers show some alignment with factors sometimes associated with **{disease_name}**. "
                    f"It may be worthwhile to mention the factors you selected to a dermatologist during a routine check-up, especially if you have concerns. "
                    f"The general information tabs below offer background context. Remember, this is not a diagnosis."
                )
            else: # Low
                st.success( # Use success color for low
                    f"**Low Educational Alignment ({alignment_percent:.0f}%):** Based on your questionnaire answers, the alignment with common factors for **{disease_name}** is low. "
                    f"While this specific condition shows low alignment based on your inputs, this tool is limited. If you have *any* skin concerns, regardless of this result, please consult a dermatologist."
                )
            # --- End Interpretation ---

            st.markdown("---")
            st.markdown("#### General Educational Information")
            disease_report_data = DISEASE_INFO[disease_name]

            st.markdown("**Genetic Risk Factors (General):**")
            st.markdown(disease_report_data.get('risk_info', 'N/A')) # Use .get()

            # Using Tabs for General Info (Layout improved by removing columns)
            info_tabs = st.tabs(["🩺 Special Care & Precautions", "✅ Helpful Ingredients (OTC)", "❌ Potential Triggers to Avoid"])

            with info_tabs[0]:
                st.markdown(disease_report_data.get('report_care', 'General skin care advice applies.'))

            with info_tabs[1]:
                st.markdown(disease_report_data.get('report_use', 'Focus on gentle, hydrating products.'))

            with info_tabs[2]:
                st.markdown(disease_report_data.get('report_avoid', 'Avoid known irritants and excessive sun exposure.'))


    st.markdown("---")

    # --- Navigation Buttons ---
    cols = st.columns(2)
    with cols[0]:
        st.button("← Back to Questionnaire", on_click=lambda: st.session_state.update(page="Step 1: Questionnaire"), type="secondary", use_container_width=True)
    with cols[1]:
        st.button("Start Over →", on_click=lambda: st.session_state.update(page="Home (Disclaimer)", diseases_to_ask=[], answers={}), type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True) # Close card-container

# --- App Structure (Single-Page Navigation) ---

# Define page structure (New Flow)
PAGES = {
    "Home (Disclaimer)": show_home,
    "Step 1: Questionnaire": show_questionnaire,
    "Step 2: Your Report": show_analysis_report
}

def setup_session_state():
    """Initializes session state variables if they don't exist."""
    if 'page' not in st.session_state:
        st.session_state.page = "Home (Disclaimer)"
    # New state variables for this flow
    if 'diseases_to_ask' not in st.session_state:
        st.session_state.diseases_to_ask = []
    # Nested dictionary: answers[disease_name][question_id] = True/False
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    # Clean up old state variables if they exist
    for key in ['family_history_selected', 'observations_selected', 'selected_disease', 'family_answers', 'symptom_answers']:
        if key in st.session_state:
            try:
                del st.session_state[key]
            except KeyError:
                pass # Already deleted or never existed


def load_css():
    """Injects custom CSS for styling the app, based on theme4.py."""
    # --- THIS FUNCTION NOW CONTAINS THE CSS FROM testui.py ---
    st.markdown(r"""
    <style>
        /* Import Google Fonts - Lora (Headings) and Source Sans Pro (Body) */
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap');

        /* "Aurora Glow" Palette (from theme4.py) */
        :root {
            --color-bg-light: #FDFBFF;     /* Soft Off-White */
            --color-bg-card: #FFFFFF;      /* White */
            --color-text-dark: #4A3F5E;    /* Dark Purple/Gray */
            --color-text-medium: #6D617A;    /* Medium Purple/Gray */
            --color-accent-purple: #957DAD; /* Elegant Purple */
            --color-gradient-start: #FFD1DC; /* Soft Pink */
            --color-gradient-end: #E0BBE4;   /* Soft Lavender */
            --color-border: #EAE6F0;       /* Light Purple/Gray Border */

            --font-heading: 'Lora', serif;
            --font-body: 'Source Sans Pro', sans-serif; /* <-- FONT CHANGED */
            --gradient-main: linear-gradient(135deg, var(--color-gradient-start) 0%, var(--color-gradient-end) 100%);
        }

        /* --- Global Styles --- */
        html, body, .stApp {
            font-family: var(--font-body);
            color: var(--color-text-medium);
            background-color: var(--color-bg-light);
            accent-color: var(--color-gradient-start); /* <-- CHECKBOX COLOR CHANGED TO PINK */
        }
        /* Center content block */
        .main .block-container {
            padding: 2rem 1rem; /* Adjust padding for smaller screens */
            max-width: 900px; /* Limit max width */
            margin: auto; /* Center */
        }
        @media (min-width: 768px) { /* Wider padding on larger screens */
             .main .block-container {
                 padding: 2rem 3rem;
             }
        }

        /* Hide default Streamlit elements */
        header[data-testid="stHeader"], footer {
            visibility: hidden;
            height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* --- MODIFICATION: Sidebar rule removed --- */


        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading);
            color: var(--color-text-dark);
            font-weight: 600;
        }
        /* Page Title */
        h1 {
            font-size: 2.5rem;
            text-align: left;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--color-border);
        }
        h2 { font-size: 2.0rem; margin-bottom: 1rem; text-align: left;} /* Page titles */
        h3 { font-size: 1.6rem; margin-bottom: 0.8rem; color: var(--color-accent-purple);} /* Section headers in report */
        h4 { font-family: var(--font-heading); color: var(--color-accent-purple); font-weight: 600; font-size: 1.3rem; margin-bottom: 0.5rem;} /* Sub-headers like Factors */

        p, li, label, .stCheckbox > label p, .stMultiSelect > label { /* Apply body font and size */
            font-size: 1.0rem;
            color: var(--color-text-medium);
            font-family: var(--font-body);
            line-height: 1.6;
        }
        ul { padding-left: 20px; margin-bottom: 1rem;}
        li { margin-bottom: 0.5rem; }
        .homepage-text {
            font-size: 1.1rem;
            color: var(--color-text-medium);
        }


        /* --- Styling for Containers (used as cards) --- */
        /* Targets the main containers on Home, Questionnaire, Report */
         .stContainer { /* Apply card style to all main page containers */
            background-color: var(--color-bg-card);
            border-radius: 20px;
            padding: 2.5rem; /* Increased padding */
            border: 1px solid var(--color-border);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        
        /* --- This rule styles the "normaal container" you requested --- */
        /* Targets containers with border=True */
        .stContainer[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--color-bg-light); /* Lighter bg for nested container */
            border: 1px dashed var(--color-border);
            box-shadow: none;
            border-radius: 15px;
            padding: 1.5rem; /* Padding inside the container */
            margin-bottom: 0.5rem; /* Space below the container */
        }


        /* Styling for Expanders in Report */
        [data-testid="stExpander"] {
             background-color: var(--color-bg-card); /* White Background */
             border-radius: 15px; /* Rounded Corners */
             border: 1px solid var(--color-border); /* Light Border */
             box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04); /* Subtle Shadow */
             margin-bottom: 1.5rem; /* Space between expanders */
             overflow: hidden; /* Prevent content overflow issues */
        }
        [data-testid="stExpander"] [data-testid="stExpanderHeader"] { /* Expander header */
            font-family: var(--font-heading);
            color: var(--color-text-dark) !important; /* Theme dark text */
            font-size: 1.2rem; /* Adjusted size */
            font-weight: 600;
            padding: 1rem 1.5rem; /* Padding for header */
            border-bottom: 1px solid var(--color-border); /* Separator line */
            background-color: #FAF7FF; /* Very light purple background for header */
        }
         [data-testid="stExpander"] [data-testid="stExpanderHeader"] p { /* Ensure text inside header matches */
             color: var(--color-text-dark) !important;
             font-weight: 600 !important;
             font-family: var(--font-heading) !important;
             font-size: 1.2rem !important;
         }
         /* Arrow color */
         [data-testid="stExpander"] [data-testid="stExpanderHeader"] svg {
             fill: var(--color-accent-purple) !important;
         }
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] { /* Expander content area */
             padding: 1.5rem; /* Padding for content */
             background-color: var(--color-bg-card); /* White background for content */
             border-radius: 0 0 15px 15px; /* Round bottom corners only */
        }
         /* Override for expanders inside questionnaire container */
         .stContainer [data-testid="stExpander"] {
             background-color: var(--color-bg-light); /* Lighter bg for nested expander */
             border: 1px dashed var(--color-border);
             box-shadow: none;
         }
         .stContainer [data-testid="stExpander"] [data-testid="stExpanderHeader"] {
             background-color: transparent; /* No bg for header in nested */
             border-bottom: 1px dashed var(--color-border);
             font-size: 1.3rem;
         }
         .stContainer [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
             background-color: transparent; /* No bg for content in nested */
         }


        /* --- Button Styles --- */
        .stButton > button {
            font-family: var(--font-body);
            font-weight: 600;
            padding: 0.7rem 1.5rem; /* Adjusted padding */
            border-radius: 30px;
            border: none;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: auto;
            min-width: 150px;
        }
        /* Primary (Gradient) */
        .stButton > button:not([kind="secondary"]) {
            background: var(--color-gradient-start) !important; /* <-- CHANGED TO LIGHT PINK */
            color: var(--color-text-dark) !important; /* Dark text */
            border: 1px solid var(--color-gradient-start) !important; /* Pink border */
            box-shadow: 0 4px 15px rgba(255, 209, 220, 0.5) !important; /* Pink shadow */
        }
        .stButton > button:not([kind="secondary"]):hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(224, 187, 228, 0.5) !important; /* Lavender shadow */
            background: var(--color-gradient-end) !important; /* Lavender background on hover */
        }
        .stButton > button:not([kind="secondary"]):disabled {
            background: var(--color-border) !important; color: var(--color-text-medium) !important;
            box-shadow: none !important; cursor: not-allowed !important; transform: none !important;
        }
        /* Secondary (Outline) */
        .stButton > button[kind="secondary"] {
            background-color: transparent; color: var(--color-accent-purple);
            border: 2px solid var(--color-accent-purple); box-shadow: none;
        }
        .stButton > button[kind="secondary"]:hover {
            background-color: var(--color-accent-purple); color: var(--color-bg-card);
            transform: translateY(-2px);
        }
        .stButton > button[kind="secondary"]:disabled {
            background-color: var(--color-bg-light); border-color: var(--color-border);
            color: var(--color-text-medium); transform: none; box-shadow: none; cursor: not-allowed;
        }

        /* --- Stepper Styles (Taskbar) --- */
        .step-box {
            background-color: var(--color-bg-card); border: 1px solid var(--color-border);
            color: var(--color-text-medium);
            padding: 12px 18px; /* <-- MADE BIGGER */
            border-radius: 15px; /* <-- MADE ROUNDER */
            text-align: center; font-weight: 500;
            transition: all 0.3s ease; font-size: 0.9rem; /* Keep font size */
            font-family: var(--font-body); margin-bottom: 1.5rem; /* Increased bottom margin */
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            min-height: 50px; /* Ensure consistent height */
            display: flex;
            align-items: center;
            justify-content: center;
        }
        /* Completed Step: Use light background and medium text color */
        .step-complete {
            background-color: var(--color-bg-light); /* Off-white */
            color: var(--color-text-medium); /* Medium Gray/Purple */
            border: 1px solid var(--color-border); /* Light border */
            font-weight: 500; /* Normal weight */
        }
        /* Active Step uses Soft Pink like testui taskbar */
        .step-active {
            background: #FFD1DC !important; /* Soft Pink */
            color: #4A3F5E !important; /* Dark Purple Text */
            border: 1px solid #FFD1DC !important; /* Pink Border */
            box-shadow: 0 4px 15px rgba(255, 209, 220, 0.5) !important;
            font-weight: 600;
        }
        /* Future Step uses default .step-box style */


        /* --- Input Styles --- */
        /* Multiselect */
        .stMultiSelect > label { /* Style label above multiselect */
            font-weight: 600;
            color: var(--color-text-dark);
            margin-bottom: 0.5rem;
            display: block; /* Ensure it takes full width */
            font-size: 1.1rem; /* Match other labels */
            font-family: var(--font-body);
        }
        .stMultiSelect [data-baseweb="select"] > div {
            background-color: var(--color-bg-light); border: 1px solid var(--color-border);
            border-radius: 15px; color: var(--color-text-dark); font-family: var(--font-body);
        }
         .stMultiSelect [data-baseweb="select"] > div:focus-within {
             border-color: var(--color-accent-purple); box-shadow: 0 0 0 2px rgba(149, 125, 173, 0.5); /* Adjusted shadow */
             background-color: var(--color-bg-card);
         }
        span[data-baseweb="tag"] {
             background-color: var(--color-accent-purple) !important; color: white !important;
             border-radius: 10px !important; font-family: var(--font-body) !important;
             font-weight: 500 !important;
             margin: 2px !important; /* Add slight margin around tags */
        }
        /* Checkbox label */
        .stCheckbox { margin-bottom: 0.75rem; } /* Add a bit more space below checkboxes */
        .stCheckbox > label {
            background-color: transparent !important; /* Ensure checkbox background isn't white */
            align-items: center; /* Vertically align checkbox and text */
        }
         .stCheckbox > label span { /* Checkbox text */
             padding-left: 0.5rem; /* Space between box and text */
             font-size: 0.95rem; /* Slightly smaller checkbox text */
         }


        /* --- Alert Boxes --- */
        .stAlert {
            border-radius: 12px; border: 1px solid var(--color-border);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); font-family: var(--font-body);
            margin-top: 1rem; margin-bottom: 1rem; /* Add vertical spacing */
        }
        .stAlert[data-baseweb="alert"] { background-color: #F6F4FF; color: #4B3F6B; border-left: 5px solid var(--color-accent-purple); }
        .stAlert[data-baseweb="alert"].st-error { background-color: #FFF0F0; color: #A83A3A; border-left: 5px solid #E57373; }
        .stAlert[data-baseweb="alert"].st-warning { background-color: #FFF9E6; color: #8C6A03; border-left: 5px solid #FFCA28; }
        .stAlert[data-baseweb="alert"].st-success { background-color: #F0FFF4; color: #38761D; border-left: 5px solid #81C784; }

        /* --- Report Tabs --- */
        [data-baseweb="tab-list"] { justify-content: start; border-bottom: 2px solid var(--color-border); gap: 1.5rem; } /* Align tabs left */
        [data-baseweb="tab"] { font-family: var(--font-heading); font-weight: 600; font-size: 1.1rem; color: var(--color-text-medium); padding-bottom: 10px; }
        [data-baseweb="tab"][aria-selected="true"] { color: var(--color-accent-purple); border-bottom-color: var(--color-accent-purple); }
        .stTabs [data-baseweb="tab-highlight"] { background-color: var(--color-accent-purple); }
        /* Tab content */
        [data-testid="stTabs"] > div:nth-child(2) > div { /* Target the tab content panel */
             background-color: var(--color-bg-light); /* Light bg for tab content */
             border: 1px solid var(--color-border);
             border-top: none;
             border-radius: 0 0 15px 15px; /* Round bottom corners */
             padding: 1.5rem;
             margin-top: -2px; /* Pull content up slightly */
        }

        /* Report Specific Text Styles */
        .stExpander h4 { /* Sub-headers like Factors */
             margin-top: 1rem;
             margin-bottom: 0.5rem;
        }
        .stExpander ul li { /* Contributing factors list */
             font-size: 0.95rem;
        }
         .stExpander ul li i { /* Dynamic info italics */
             color: var(--color-text-medium);
         }
         .stExpander .stCaption { /* Breakdown caption */
             font-size: 0.85rem;
             color: var(--color-text-medium);
         }
         /* General info tabs content */
         [data-testid="stTabs"] [data-testid="stVerticalBlock"] p,
         [data-testid="stTabs"] [data-testid="stVerticalBlock"] li {
             font-size: 0.95rem;
             line-height: 1.7; /* Improve readability in tabs */
         }
          [data-testid="stTabs"] [data-testid="stVerticalBlock"] strong {
             color: var(--color-text-dark); /* Make bold text darker in tabs */
          }

         /* Specific styles for title block */
         .title-container {
             text-align:center;
             margin-top:0rem;
             margin-bottom:1.5rem;
         }
         .title-main {
             font-family: 'Lora', serif; color:#4A3F5E; font-weight:650; letter-spacing:1px;
             font-size:clamp(2.2rem, 6.1vw, 3.0rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);
         }
          .title-sub {
             font-family: 'Lora', serif; color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase;
             font-size:clamp(1.0rem, 3.5vw, 1.8rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);
          }

         /* Footer */
         .footer-disclaimer {
             text-align: center; font-size: 0.85rem; color: var(--color-text-medium); padding: 3rem 1rem 1rem 1rem;
         }
         hr {
             border-top: 1px solid var(--color-border); /* Lighten dividers */
             margin-top: 1rem;
             margin-bottom: 1rem;
         }
         
         /* Fix for expander content background override */
         .stContainer [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
             background-color: var(--color-bg-light) !important; /* Lighter bg for nested expander content */
         }

         /* Fix for new questionnaire container */
         .stContainer[data-testid="stVerticalBlockBorderWrapper"] .stCheckbox > label span {
             color: var(--color-text-medium); /* Ensure checkbox text is correct color */
         }
         .stContainer[data-testid="stVerticalBlockBorderWrapper"] strong {
             color: var(--color-text-dark); /* Ensure bold text is correct color */
         }

    </style>
    """, unsafe_allow_html=True)

def show_stepper(current_page_key):
    """Displays a visual stepper at the top of the page."""
    page_keys = list(PAGES.keys())
    current_index = page_keys.index(current_page_key)

    step_cols = st.columns(len(page_keys))

    for i, (key, col) in enumerate(zip(page_keys, step_cols)):
        with col:
            # Adjust label for the new flow
            step_label = key.split(': ')[-1] # Get text after ": "
            if i < current_index:
                # Completed step
                label = f"✓ {step_label}"
                st.markdown(f"<div class='step-box step-complete'>{label}</div>", unsafe_allow_html=True)
            elif i == current_index:
                # Current active step
                label = step_label
                st.markdown(f"<div class='step-box step-active'>{label}</div>", unsafe_allow_html=True)
            else:
                # Future step
                label = step_label
                st.markdown(f"<div class='step-box'>{label}</div>", unsafe_allow_html=True) # Use default style (light background)

    st.markdown("<br>", unsafe_allow_html=True) # Add some space

# --- Main App Logic ---

def main():
    """Main function to run the Streamlit app."""

    # Set up page configuration
    st.set_page_config(page_title="Genetic Skin Health Educator", layout="wide", initial_sidebar_state="auto") # Changed to "auto"

    # Load custom CSS
    load_css()

    # Initialize session state
    setup_session_state()

    # --- Title (Applied from Theme) ---
    st.markdown("""
    <div class="title-container">
        <div class="title-sub">Genetic Skin Health</div>
        <div class="title-main">Educational Tool</div>
    </div>
    """, unsafe_allow_html=True)


    # Map page key to page-rendering function
    page_function = PAGES[st.session_state.page]

    # Run the function corresponding to the current page
    # Wrap page content in a main container for consistent card styling
    # --- Apply card styling to the main container wrapper ---
    # st.markdown('<div class="card-container">', unsafe_allow_html=True) # Removed redundant wrapper
    page_function()
    # st.markdown('</div>', unsafe_allow_html=True) # Removed redundant wrapper
    # --- End card styling wrapper ---


    # Footer Disclaimer
    st.markdown(
        '<div class="footer-disclaimer">⚠️ **Disclaimer:** This tool provides educational information based on general associations and is not medical advice. Consult a dermatologist for diagnosis and treatment.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()