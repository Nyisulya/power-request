document.addEventListener("DOMContentLoaded", () => {
    // 1. Language Handling System
    const welcomeScreen = document.getElementById("welcome-screen");
    const langSelectSw = document.getElementById("lang-select-sw");
    const langSelectEn = document.getElementById("lang-select-en");
    const navBtnSw = document.getElementById("nav-btn-sw");
    const navBtnEn = document.getElementById("nav-btn-en");

    function setLanguage(lang) {
        localStorage.setItem("lang_pref", lang);
        document.body.className = `lang-active-${lang}`;
        
        // Update nav buttons active states
        if (navBtnSw && navBtnEn) {
            if (lang === "sw") {
                navBtnSw.classList.add("active");
                navBtnEn.classList.remove("active");
            } else {
                navBtnEn.classList.add("active");
                navBtnSw.classList.remove("active");
            }
        }
    }

    // Initialize language
    const storedLang = localStorage.getItem("lang_pref");
    if (storedLang) {
        setLanguage(storedLang);
        if (welcomeScreen) {
            welcomeScreen.classList.add("hidden");
        }
    } else {
        // First time visitor, show welcome screen
        if (welcomeScreen) {
            welcomeScreen.classList.remove("hidden");
        }
    }

    // Welcome Screen step transition and registration handling
    const step1 = document.getElementById("welcome-step-1");
    const step2 = document.getElementById("welcome-step-2");
    const btnSkipReg = document.getElementById("btn-skip-registration");
    const regForm = document.getElementById("welcome-registration-form");

    function closeWelcomeScreen() {
        if (welcomeScreen) {
            welcomeScreen.classList.add("hidden");
            // Reset skip/close button text
            if (btnSkipReg) {
                const enSpan = btnSkipReg.querySelector(".lang-en");
                const swSpan = btnSkipReg.querySelector(".lang-sw");
                if (enSpan) enSpan.textContent = "Skip & Enter";
                if (swSpan) swSpan.textContent = "Ruka na Ingia";
            }
        }
    }

    if (langSelectSw) {
        langSelectSw.addEventListener("click", () => {
            setLanguage("sw");
            if (step1 && step2) {
                step1.classList.add("hidden");
                step2.classList.remove("hidden");
            } else {
                closeWelcomeScreen();
            }
        });
    }
    if (langSelectEn) {
        langSelectEn.addEventListener("click", () => {
            setLanguage("en");
            if (step1 && step2) {
                step1.classList.add("hidden");
                step2.classList.remove("hidden");
            } else {
                closeWelcomeScreen();
            }
        });
    }

    // Bind triggers to open Step 2 directly (e.g. from navbar "Join Family")
    const registerTriggers = document.querySelectorAll(".btn-trigger-register");
    registerTriggers.forEach(trigger => {
        trigger.addEventListener("click", () => {
            if (welcomeScreen && step2) {
                if (step1) step1.classList.add("hidden");
                step2.classList.remove("hidden");
                welcomeScreen.classList.remove("hidden");

                // Customize skip button text to act as "Close"
                if (btnSkipReg) {
                    const enSpan = btnSkipReg.querySelector(".lang-en");
                    const swSpan = btnSkipReg.querySelector(".lang-sw");
                    if (enSpan) enSpan.textContent = "Close";
                    if (swSpan) swSpan.textContent = "Funga";
                }
            }
        });
    });

    if (btnSkipReg) {
        btnSkipReg.addEventListener("click", () => {
            closeWelcomeScreen();
        });
    }

    if (regForm) {
        regForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(regForm);
            
            fetch("/register/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    localStorage.setItem("follower_name", data.full_name);
                    localStorage.setItem("follower_country", data.country);
                    localStorage.setItem("follower_identifier", data.identifier);
                    applyStoredIdentity();
                }
                closeWelcomeScreen();
            })
            .catch(err => {
                console.error(err);
                closeWelcomeScreen(); // Proceed anyway so they aren't blocked
            });
        });
    }

    // Nav bar language toggle listeners
    if (navBtnSw) {
        navBtnSw.addEventListener("click", () => setLanguage("sw"));
    }
    if (navBtnEn) {
        navBtnEn.addEventListener("click", () => setLanguage("en"));
    }

    // Identity persistence helper
    function applyStoredIdentity() {
        const name = localStorage.getItem("follower_name");
        const country = localStorage.getItem("follower_country");
        const identifier = localStorage.getItem("follower_identifier");
        
        if (name && country) {
            const reqAuthor = document.getElementById("req-author");
            const reqCountry = document.getElementById("req-country");
            const testAuthor = document.getElementById("test-author");
            const testCountry = document.getElementById("test-country");
            
            if (reqAuthor && !reqAuthor.value) reqAuthor.value = name;
            if (reqCountry && !reqCountry.value) reqCountry.value = country;
            if (testAuthor && !testAuthor.value) testAuthor.value = name;
            if (testCountry && !testCountry.value) testCountry.value = country;
        }
        
        if (identifier) {
            const quizIdentifier = document.getElementById("quiz-identifier");
            if (quizIdentifier) {
                quizIdentifier.value = identifier;
                quizIdentifier.style.display = "none";
                // Optionally hide the helper text too to make it super clean
                const authDesc = quizIdentifier.parentElement.previousElementSibling;
                if (authDesc && authDesc.tagName === 'P') {
                    const isSw = localStorage.getItem("lang_pref") === "sw";
                    authDesc.innerHTML = isSw ? "<b>Tayari umeshasajiliwa!</b> Bonyeza 'Anza Swali' kujibu." : "<b>You are registered!</b> Click 'Start Quiz' to begin.";
                }
            }
        }
    }
    
    // Apply identity if previously saved
    applyStoredIdentity();

    // 2. Tab switching logic (Requests vs Testimonies forms)
    const tabRequestBtn = document.getElementById("tab-request-btn");
    const tabTestimonyBtn = document.getElementById("tab-testimony-btn");
    const panelRequest = document.getElementById("panel-request");
    const panelTestimony = document.getElementById("panel-testimony");

    if (tabRequestBtn && tabTestimonyBtn) {
        tabRequestBtn.addEventListener("click", () => {
            tabRequestBtn.classList.add("active");
            tabTestimonyBtn.classList.remove("active");
            panelRequest.classList.add("active");
            panelTestimony.classList.remove("active");
        });

        tabTestimonyBtn.addEventListener("click", () => {
            tabTestimonyBtn.classList.add("active");
            tabRequestBtn.classList.remove("active");
            panelTestimony.classList.add("active");
            panelRequest.classList.remove("active");
        });
    }

    // 3. Timezone formatting & Countdown Timer
    const prayerTimeContainer = document.getElementById("prayer-time-container");
    if (prayerTimeContainer) {
        const utcTimeStr = prayerTimeContainer.getAttribute("data-utc-time");
        const liveBadge = document.getElementById("live-badge");
        const timeValSw = document.getElementById("time-value-sw");
        const timeValEn = document.getElementById("time-value-en");
        const timezoneVal = document.getElementById("timezone-value");
        const countdownSw = document.getElementById("countdown-value-sw");
        const countdownEn = document.getElementById("countdown-value-en");

        if (utcTimeStr) {
            const prayerDate = new Date(utcTimeStr);

            if (!isNaN(prayerDate.getTime())) {
                // Show localized datetime
                const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                timezoneVal.textContent = browserTimezone;

                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
                timeValEn.textContent = new Intl.DateTimeFormat('en-US', options).format(prayerDate);
                timeValSw.textContent = new Intl.DateTimeFormat('sw', options).format(prayerDate);

                // Countdown Timer updates
                function updateCountdown() {
                    const now = new Date();
                    const diffMs = prayerDate - now;

                    if (diffMs > 0) {
                        // Future: show countdown
                        liveBadge.className = "live-badge-glow";
                        liveBadge.querySelector(".lang-en").textContent = "Upcoming Session";
                        liveBadge.querySelector(".lang-sw").textContent = "Ibada Inayokuja";

                        const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
                        const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                        const diffSecs = Math.floor((diffMs % (1000 * 60)) / 1000);

                        countdownEn.textContent = `Starts in: ${diffHrs}h ${diffMins}m ${diffSecs}s`;
                        countdownSw.textContent = `Inaanza baada ya: saa ${diffHrs}, dk ${diffMins}, sek ${diffSecs}`;
                    } else {
                        // Present or past: check if currently live (within 2 hours of start)
                        const liveDurationMs = 2 * 60 * 60 * 1000; // 2 hours
                        if (now - prayerDate < liveDurationMs) {
                            liveBadge.className = "live-badge-glow active";
                            liveBadge.querySelector(".lang-en").textContent = "LIVE NOW";
                            liveBadge.querySelector(".lang-sw").textContent = "IBADA INAENDELEA";

                            countdownEn.textContent = "Live worship in progress! Click Join Live above.";
                            countdownSw.textContent = "Ibada inaendelea sasa hivi! Bonyeza kitufe hapo juu kuungana.";
                        } else {
                            // Long past
                            liveBadge.className = "live-badge-glow";
                            liveBadge.querySelector(".lang-en").textContent = "Completed";
                            liveBadge.querySelector(".lang-sw").textContent = "Imekamilika";

                            countdownEn.textContent = "The scheduled session is completed. Next update soon.";
                            countdownSw.textContent = "Ibada iliyopangwa imekamilika. Kikao kijacho hivi karibuni.";
                        }
                    }
                }

                updateCountdown();
                setInterval(updateCountdown, 1000);
            } else {
                // If invalid or empty prayer date
                countdownEn.textContent = "Next session will be scheduled soon.";
                countdownSw.textContent = "Ibada ijayo itapangwa hivi karibuni.";
            }
        }
    }

    // Helper to get CSRF token from cookies (with DOM input fallback for fresh sessions)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        if (!cookieValue && name === 'csrftoken') {
            const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (tokenInput) {
                cookieValue = tokenInput.value;
            }
        }
        return cookieValue;
    }

    // 4. AJAX Form Submission: Prayer Requests
    const formRequest = document.getElementById("form-request");
    const reqListContainer = document.getElementById("requests-list-container");
    const reqCountBadge = document.getElementById("requests-count-badge");

    if (formRequest) {
        formRequest.addEventListener("submit", (e) => {
            e.preventDefault();
            const submitBtn = formRequest.querySelector('button[type="submit"]');
            const authorInput = document.getElementById("req-author");
            const contentInput = document.getElementById("req-content");
            const countryInput = document.getElementById("req-country");

            if (!contentInput.value.trim()) return;

            submitBtn.disabled = true;
            submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Inatuma..." : "Sending...";

            const formData = new FormData();
            formData.append("author_name", authorInput.value);
            formData.append("content", contentInput.value);
            formData.append("user_country", countryInput.value);

            fetch("/submit-request/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Tuma Ombi la Maombi" : "Send Prayer Request";

                if (data.success) {
                    contentInput.value = "";
                    authorInput.value = "";

                    // Add new card dynamically
                    const card = document.createElement("div");
                    card.className = "feed-card slide-down-card";
                    card.innerHTML = `
                        <div class="feed-meta">
                            <div class="feed-author">
                                👤 <span>${data.author_name}</span>
                                <span class="feed-country">${data.user_country}</span>
                            </div>
                            <div class="feed-date">
                                🕒 <span class="lang-en">Just now</span><span class="lang-sw">Sasa hivi</span>
                            </div>
                        </div>
                        <div class="feed-body lang-en">${data.content_en}</div>
                        <div class="feed-body lang-sw">${data.content_sw}</div>
                    `;
                    
                    if (reqListContainer) {
                        const noMsg = reqListContainer.querySelector(".no-entries");
                        if (noMsg) noMsg.remove();
                        reqListContainer.insertBefore(card, reqListContainer.firstChild);

                        // Increment badge counter
                        if (reqCountBadge) {
                            let cnt = parseInt(reqCountBadge.textContent) || 0;
                            reqCountBadge.textContent = cnt + 1;
                        }
                    }
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                submitBtn.disabled = false;
                submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Tuma Ombi la Maombi" : "Send Prayer Request";
                alert("Failed to submit request. Please try again.");
            });
        });
    }

    // 5. AJAX Form Submission: Testimonies
    const formTestimony = document.getElementById("form-testimony");
    const testListContainer = document.getElementById("testimonies-list-container");
    const testCountBadge = document.getElementById("testimonies-count-badge");

    if (formTestimony) {
        formTestimony.addEventListener("submit", (e) => {
            e.preventDefault();
            const submitBtn = formTestimony.querySelector('button[type="submit"]');
            const authorInput = document.getElementById("test-author");
            const contentInput = document.getElementById("test-content");
            const countryInput = document.getElementById("test-country");

            if (!contentInput.value.trim()) return;

            submitBtn.disabled = true;
            submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Inatuma..." : "Sending...";

            const formData = new FormData();
            formData.append("author_name", authorInput.value);
            formData.append("content", contentInput.value);
            formData.append("user_country", countryInput.value);

            fetch("/submit-testimony/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Tuma Ushuhuda Wako" : "Share Testimony";

                if (data.success) {
                    contentInput.value = "";
                    authorInput.value = "";

                    // Add new card dynamically
                    const card = document.createElement("div");
                    card.className = "feed-card testimony-card slide-down-card";
                    card.innerHTML = `
                        <div class="feed-meta">
                            <div class="feed-author">
                                👤 <span>${data.author_name}</span>
                                <span class="feed-country">${data.user_country}</span>
                            </div>
                            <div class="feed-date">
                                🕒 <span class="lang-en">Just now</span><span class="lang-sw">Sasa hivi</span>
                            </div>
                        </div>
                        <div class="feed-body lang-en">${data.content_en}</div>
                        <div class="feed-body lang-sw">${data.content_sw}</div>
                    `;

                    if (testListContainer) {
                        const noMsg = testListContainer.querySelector(".no-entries");
                        if (noMsg) noMsg.remove();
                        testListContainer.insertBefore(card, testListContainer.firstChild);

                        // Increment badge counter
                        if (testCountBadge) {
                            let cnt = parseInt(testCountBadge.textContent) || 0;
                            testCountBadge.textContent = cnt + 1;
                        }
                    }
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                submitBtn.disabled = false;
                submitBtn.textContent = localStorage.getItem("lang_pref") === "sw" ? "Tuma Ushuhuda Wako" : "Share Testimony";
                alert("Failed to submit testimony. Please try again.");
            });
        });
    }

    // 6. Leader Admin Panel: DateTime translation & Row deletion
    const leaderForm = document.getElementById("leader-settings-form");
    if (leaderForm) {
        leaderForm.addEventListener("submit", (e) => {
            const localTimeInput = document.getElementById("prayer_time_local");
            const hiddenTimeInput = document.getElementById("prayer_time_utc");

            if (localTimeInput && localTimeInput.value) {
                // Convert browser's local time selection to UTC ISO string
                const localDateObj = new Date(localTimeInput.value);
                if (!isNaN(localDateObj.getTime())) {
                    hiddenTimeInput.value = localDateObj.toISOString();
                }
            }
        });

        // Set the localized initial value in datetime-local if exists
        const localTimeInput = document.getElementById("prayer_time_local");
        const hiddenTimeInput = document.getElementById("prayer_time_utc");
        if (localTimeInput && hiddenTimeInput && hiddenTimeInput.value) {
            const initialUtcDate = new Date(hiddenTimeInput.value);
            if (!isNaN(initialUtcDate.getTime())) {
                // Formatting date to 'yyyy-MM-ddThh:mm' for datetime-local value
                const tzOffset = initialUtcDate.getTimezoneOffset() * 60000;
                const localISOTime = (new Date(initialUtcDate - tzOffset)).toISOString().slice(0, 16);
                localTimeInput.value = localISOTime;
            }
        }
    }

    // AJAC Row Deletion in Leader Panel
    const deleteButtons = document.querySelectorAll(".btn-delete");
    deleteButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const type = btn.getAttribute("data-type");
            const cardElement = btn.closest(".feed-card");

            if (confirm(localStorage.getItem("lang_pref") === "sw" ? "Una uhakika unataka kufuta hii?" : "Are you sure you want to delete this?")) {
                const formData = new FormData();
                let deleteAction = "delete_request";
                if (type === "testimony") deleteAction = "delete_testimony";
                else if (type === "announcement") deleteAction = "delete_announcement";
                else if (type === "leader") deleteAction = "delete_leader";
                else if (type === "follower") deleteAction = "delete_follower";
                
                formData.append("action", deleteAction);
                formData.append("id", id);

                fetch("/leader/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: formData
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        cardElement.style.opacity = '0';
                        setTimeout(() => {
                            cardElement.remove();
                        }, 300);
                    } else {
                        alert("Delete failed.");
                    }
                })
                .catch(err => console.error(err));
            }
        });
    });

    // 7. Daily recurring schedule timezone formatting
    const scheduleItems = document.querySelectorAll(".schedule-item");
    scheduleItems.forEach(item => {
        const utcHour = parseInt(item.getAttribute("data-utc-hour"));
        const utcMinute = parseInt(item.getAttribute("data-utc-minute"));
        
        // Create date object representing today at that UTC time
        const sessionDate = new Date();
        sessionDate.setUTCHours(utcHour, utcMinute, 0, 0);

        const localTimeVal = item.querySelector(".schedule-time-local");
        if (localTimeVal) {
            const timeOptions = { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' };
            const formattedTimeEn = new Intl.DateTimeFormat('en-US', timeOptions).format(sessionDate);
            const formattedTimeSw = new Intl.DateTimeFormat('sw', timeOptions).format(sessionDate);
            
            localTimeVal.innerHTML = `
                <span class="lang-en">Your Time: ${formattedTimeEn}</span>
                <span class="lang-sw">Muda Wako: ${formattedTimeSw}</span>
            `;
        }

        // Highlight if session is active now (within 1.5 hours of start time)
        const now = new Date();
        const sessionStartToday = new Date(now);
        sessionStartToday.setUTCHours(utcHour, utcMinute, 0, 0);
        
        const sessionEndToday = new Date(sessionStartToday.getTime() + 1.5 * 60 * 60 * 1000);
        if (now >= sessionStartToday && now <= sessionEndToday) {
            item.classList.add("active-session");
        }
    });

    // 8. Clipboard Copy Helper
    const copyButtons = document.querySelectorAll(".btn-copy-clipboard");
    copyButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const textToCopy = btn.getAttribute("data-copy");
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalTextEn = btn.querySelector(".btn-copy-text-en") ? btn.querySelector(".btn-copy-text-en").textContent : "Copy";
                    const originalTextSw = btn.querySelector(".btn-copy-text-sw") ? btn.querySelector(".btn-copy-text-sw").textContent : "Nakili";

                    if (btn.querySelector(".btn-copy-text-en")) btn.querySelector(".btn-copy-text-en").textContent = "Copied!";
                    if (btn.querySelector(".btn-copy-text-sw")) btn.querySelector(".btn-copy-text-sw").textContent = "Imenakiliwa!";

                    btn.style.borderColor = "var(--success)";
                    btn.style.color = "var(--success)";

                    setTimeout(() => {
                        if (btn.querySelector(".btn-copy-text-en")) btn.querySelector(".btn-copy-text-en").textContent = originalTextEn;
                        if (btn.querySelector(".btn-copy-text-sw")) btn.querySelector(".btn-copy-text-sw").textContent = originalTextSw;
                        btn.style.borderColor = "";
                        btn.style.color = "";
                    }, 2000);
                }).catch(err => {
                    console.error("Failed to copy: ", err);
                });
            }
        });
    });
    // 9. Light/Dark Theme Toggle
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const iconDark = document.getElementById("theme-icon-dark");
    const iconLight = document.getElementById("theme-icon-light");

    function setThemeMode(mode) {
        if (mode === 'light') {
            document.documentElement.classList.add('theme-light');
            document.body.classList.add('theme-light');
            if (iconDark) iconDark.style.display = 'inline';
            if (iconLight) iconLight.style.display = 'none';
        } else {
            document.documentElement.classList.remove('theme-light');
            document.body.classList.remove('theme-light');
            if (iconDark) iconDark.style.display = 'none';
            if (iconLight) iconLight.style.display = 'inline';
        }
        localStorage.setItem("theme_mode", mode);
    }

    if (themeToggleBtn) {
        // Initialize from local storage
        const storedTheme = localStorage.getItem("theme_mode");
        if (storedTheme === 'light') {
            setThemeMode('light');
        }

        themeToggleBtn.addEventListener("click", () => {
            const currentMode = document.body.classList.contains('theme-light') ? 'light' : 'dark';
            const newMode = currentMode === 'light' ? 'dark' : 'light';
            setThemeMode(newMode);
        });
    }

    // 10. Daily Quiz Logic
    const btnStartQuiz = document.getElementById("btn-start-quiz");
    const quizAuthSection = document.getElementById("quiz-auth-section");
    const quizActiveSection = document.getElementById("quiz-active-section");
    const quizResultSection = document.getElementById("quiz-result-section");
    const btnSubmitQuiz = document.getElementById("btn-submit-quiz");
    let quizTimerInterval = null;
    let quizStartTime = null;
    let currentFollowerId = null;

    if (btnStartQuiz) {
        btnStartQuiz.addEventListener("click", () => {
            const identifier = document.getElementById("quiz-identifier").value.trim();
            const qid = btnStartQuiz.getAttribute("data-qid");
            const errDiv = document.getElementById("quiz-auth-error");
            
            if (!identifier) {
                errDiv.textContent = localStorage.getItem("lang_pref") === "sw" ? "Tafadhali weka namba au email." : "Please enter your number or email.";
                errDiv.style.display = "block";
                return;
            }
            
            btnStartQuiz.disabled = true;
            
            const formData = new FormData();
            formData.append("identifier", identifier);
            formData.append("question_id", qid);
            
            fetch("/quiz/start/", {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                btnStartQuiz.disabled = false;
                if (data.success) {
                    currentFollowerId = data.follower_id;
                    errDiv.style.display = "none";
                    quizAuthSection.style.display = "none";
                    quizActiveSection.style.display = "block";
                    
                    // Start timer
                    quizStartTime = Date.now();
                    const timerDisplay = document.getElementById("quiz-timer-display");
                    timerDisplay.style.display = "block";
                    quizTimerInterval = setInterval(() => {
                        const seconds = ((Date.now() - quizStartTime) / 1000).toFixed(1);
                        timerDisplay.textContent = seconds + "s";
                    }, 100);
                    
                } else {
                    errDiv.textContent = data.error;
                    errDiv.style.display = "block";
                }
            })
            .catch(err => {
                btnStartQuiz.disabled = false;
                console.error(err);
            });
        });
    }

    if (btnSubmitQuiz) {
        btnSubmitQuiz.addEventListener("click", () => {
            const answer = document.getElementById("quiz-answer-input").value.trim();
            const qid = btnSubmitQuiz.getAttribute("data-qid");
            const errDiv = document.getElementById("quiz-submit-error");
            
            if (!answer) return;
            
            btnSubmitQuiz.disabled = true;
            if (quizTimerInterval) clearInterval(quizTimerInterval);
            
            const formData = new FormData();
            formData.append("follower_id", currentFollowerId);
            formData.append("question_id", qid);
            formData.append("answer_text", answer);
            
            fetch("/quiz/submit/", {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                quizActiveSection.style.display = "none";
                quizResultSection.style.display = "block";
                document.getElementById("quiz-timer-display").style.display = "none";
                
                const title = document.getElementById("quiz-result-title");
                const desc = document.getElementById("quiz-result-desc");
                const isSw = localStorage.getItem("lang_pref") === "sw";
                
                if (data.success) {
                    if (data.is_correct) {
                        quizResultSection.style.background = "rgba(16, 185, 129, 0.1)";
                        quizResultSection.style.border = "1px solid var(--success)";
                        title.style.color = "var(--success)";
                        title.textContent = isSw ? "Sahihi Kabisa! 🎉" : "Correct! 🎉";
                        desc.textContent = isSw ? `Umetumia sekunde ${data.time_taken}. Kasi nzuri!` : `You took ${data.time_taken} seconds. Great speed!`;
                    } else {
                        quizResultSection.style.background = "rgba(239, 68, 68, 0.1)";
                        quizResultSection.style.border = "1px solid var(--danger)";
                        title.style.color = "var(--danger)";
                        title.textContent = isSw ? "Umekosa 😔" : "Incorrect 😔";
                        desc.textContent = isSw ? `Jibu sahihi lilikuwa: "${data.correct_answer}"` : `The correct answer was: "${data.correct_answer}"`;
                    }
                } else {
                    title.textContent = "Error";
                    desc.textContent = data.error;
                }
            })
            .catch(err => console.error(err));
        });
    }
});
