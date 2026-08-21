/**
 * Frontend Controller for Discord Queue Joiner (Dedicated CUSTOM SERVERS Tab, Volume Control, Silent Anti-Screenshot Protection, Auto-Detect Token, Webhook Alerts & Multi-Channel)
 */
(function() {
    let pyApi = null;
    let currentConfig = {};
    let logLinesCount = 0;
    let activeLogFilter = 'all';
    let activeClickMode = 'turbo';

    const modeDescriptions = {
        "turbo": {
            title: "TURBO clicks",
            desc: "The second a tester flips online, Queue Sniper fires Join before you could reach your mouse. TURBO is the default because speed is the whole point.",
            icon: "fa-solid fa-bolt"
        },
        "smart": {
            title: "Smart mode",
            desc: "Smart mode reads the moment. It hits fast when the coast is clear and eases off when a tester lingers, so you stay quick without ever looking like a bot.",
            icon: "fa-solid fa-brain"
        },
        "patience": {
            title: "Patience mode",
            desc: "Patience mode waits a beat so your Join lands naturally inside the rush instead of a split-second early. Perfect when testers watch for instant clickers.",
            icon: "fa-solid fa-clock"
        },
        "safe": {
            title: "Ultra Safe mode",
            desc: "Ultra Safe is your stealth setting. Randomised, human-like delays make every click look hand-made, for when protecting your account comes first.",
            icon: "fa-solid fa-shield-halved"
        }
    };

    const defaultMctiersChannels = {
        "crystal": { enabled: true, name: "McTiers Crystal", server_id: "898743810207653919", channel_id: "898743810207653919", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/4Y4yKdubuCrgZCEF1om__A5XVeLrMfZF23-sj6KArW4/https/cdn.discordapp.com/icons/898743810207653919/f0567dc82a9fd0728bf75c23790a5327.png?format=webp&quality=lossless" },
        "sw": { enabled: true, name: "McTiers Sw", server_id: "1317975081976332338", channel_id: "1317975085470187623", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/xXYKolnRFyE1tpoh8nG3_isKzefvgAYs2LuLHfipnZ8/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317975081976332338/fee96fb5d4c69bc55a400023dbf839b8.png?format=webp&quality=lossless" },
        "smp": { enabled: true, name: "McTiers Smp", server_id: "1224245679749206050", channel_id: "1224245683335462969", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/GjRgcD2jdEiHrO_QSbZ7XeWF5c299CKottpFgBIrkVs/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1224245679749206050/137e5c98c628b454504ca99c0d6a9536.png?format=webp&quality=lossless&width=192&height=192" },
        "netherite_pot": { enabled: true, name: "McTiers NethPot", server_id: "1317971630886227998", channel_id: "1317971632484126791", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/YIyMU7GUG8ZvRmczbKgHgw-yl1yDZmUtCKC3avY776M/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317971630886227998/3f472c84b0be45061b005e17c0a109f4.png?format=webp&quality=lossless" },
        "dia_pot": { enabled: true, name: "McTiers DiaPot", server_id: "1317974023384334426", channel_id: "1317974027922309133", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/onAdwdICQ8zFfLVNI6Z3rHEMzCHwByToNLUAmyB6_co/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317974023384334426/2af41699c1ccaa3f072d533c6610bb4a.png?format=webp&quality=lossless" },
        "uhc": { enabled: true, name: "McTiers UHC", server_id: "1316948661384646767", channel_id: "1316948663095791623", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/xgdVDQGxwBupAb2MlnXKFmFDjX_YlxnYedx5jVqQ4yk/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1316948661384646767/c4a4637ee780847a8bed935b23ceb290.png?format=webp&quality=lossless&width=192&height=192" },
        "mace": { enabled: true, name: "McTiers Mace", server_id: "1187058381849112606", channel_id: "1306853800547581963", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/baqkLlJkn0RJlIhNgRT3y-lNIjF6H5BqxmKK5Y78lkg/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1187058381849112606/2aaa555030ca7f61560b89cc00880e20.png?format=webp&quality=lossless" },
        "axe_shield": { enabled: true, name: "McTiers Axe & Shield", server_id: "1317974470132240424", channel_id: "1317974473617707094", bot_id: "1124128173609713734", logo: "https://images-ext-1.discordapp.net/external/ix7udav1xOhuiEz3Gesk2baZE6gi8XaD-IkV1_EvFWc/%3Fsize%3D4096/https/cdn.discordapp.com/icons/1317974470132240424/9d4311fbe3d8cd980473555284bf595d.png?format=webp&quality=lossless" }
    };

    const defaultPvptiersChannels = {
        "crystal": { enabled: true, name: "PvPtiers Crystal", server_id: "898743810207653919", channel_id: "1333182374271254568", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/knNxKpXjuLt9ojuCI57YzZxuP1kYqq7PlYeqFuJv7ic/%3Fsize%3D512/https/cdn.discordapp.com/icons/1333178700883034269/ef652f451a176ff1fe9d6d4449315dc1.png?format=webp&quality=lossless" },
        "sword": { enabled: true, name: "PvPtiers Sword", server_id: "513709294844117013", channel_id: "984399701904347197", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/UA_PSb2gcroZmeLAHsH7KB4eJM2u7YnyG45XG4GJa9w/%3Fsize%3D512/https/cdn.discordapp.com/icons/513709294844117013/d416c244360a171124c92354a142604d.png?format=webp&quality=lossless" },
        "smp": { enabled: true, name: "PvPtiers SMP", server_id: "981948043903533176", channel_id: "1059958212687839382", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/DKJUBn3vRQDahdZtBM7xITNCeMuhC-G1smDeerfBiB0/%3Fsize%3D512/https/cdn.discordapp.com/icons/981948043903533176/a5edb1bf548326547f356a051c3f965a.png?format=webp&quality=lossless" },
        "nethpot": { enabled: true, name: "PvPtiers NethPot", server_id: "875309328607899658", channel_id: "1005941425793400863", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/D1McPf4EItXyOsjouYLIix1-DFifAhwV6voIs8nu1AY/%3Fsize%3D512/https/cdn.discordapp.com/icons/875309328607899658/80182749367c293a6c6ff6318aadb9c4.png?format=webp&quality=lossless&width=320&height=320" },
        "diapot": { enabled: true, name: "PvPtiers DiaPot", server_id: "1007038689412665404", channel_id: "1125430210200862772", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/GjaafFAcS7yevb5sMGbMvAeODdMzoSgznlDJoz9JR9c/%3Fsize%3D512/https/cdn.discordapp.com/icons/1007038689412665404/c1f795f90a215dff4faec5d259ad9135.png?format=webp&quality=lossless" },
        "uhc": { enabled: true, name: "PvPtiers UHC", server_id: "860880412975824898", channel_id: "1012663179697991733", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/0AOVdtPR3IKR7WYsq8KpXmczV0B5HOstw9vygy8KE8M/%3Fsize%3D512/https/cdn.discordapp.com/icons/860880412975824898/4e3b3454978a0157484a261c23adc607.png?format=webp&quality=lossless" },
        "mace": { enabled: true, name: "PvPtiers Mace", server_id: "1187058381849112606", channel_id: "1395704405977862144", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/wCVxoqwEBXPfWj-_WQOgRRoD5zjcEgoG9t-qZsiIFXE/%3Fsize%3D512/https/cdn.discordapp.com/icons/1345939343448997908/68d2cca9dbacb84cb9cb6f0db72b2676.png?format=webp&quality=lossless&width=320&height=320" },
        "axe": { enabled: true, name: "PvPtiers Axe", server_id: "896903597709754398", channel_id: "1060546468580184114", bot_id: "1328378417145446440", logo: "https://images-ext-1.discordapp.net/external/x5GJ3J_irDD7lJm6z5Ob-khjeeYGNS8AWuT0Je_rfSY/%3Fsize%3D512/https/cdn.discordapp.com/icons/896903597709754398/eb1a1048d3f7fb738dd1849163025c0b.png?format=webp&quality=lossless" }
    };

    const defaultCustomChannels = {
        "custom_1": { enabled: true, name: "Custom Server 1", server_id: "", channel_id: "", bot_id: "", isCustom: true }
    };

    let activeMctiersChannels = Object.assign({}, defaultMctiersChannels);
    let activePvptiersChannels = Object.assign({}, defaultPvptiersChannels);
    let activeCustomChannels = Object.assign({}, defaultCustomChannels);

    // Play Alert Sound with exact volume scaling
    window.playAlertSound = function(volumePercent = 80) {
        if (volumePercent <= 0) return;
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            const maxGain = (volumePercent / 100) * 0.5;
            gain.gain.setValueAtTime(0.01, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(maxGain, ctx.currentTime + 0.04);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
            osc.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.15); // E6

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.35);
        } catch (e) {
            console.error("Play alert sound error:", e);
        }
    };

    // Wait for pywebviewready
    window.addEventListener('pywebviewready', function() {
        if (window.pywebview && window.pywebview.api) {
            pyApi = window.pywebview.api;
            addLogLine('System', 'PyWebView API connected successfully.', 'system');
            loadInitialConfig();

            setInterval(pollLogs, 200);
            setInterval(pollStatuses, 200);
        }
    });

    // DOM Elements
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const logTerminal = document.getElementById('logTerminal');
    const logCountBadge = document.getElementById('logCount');

    // Volume Slider Controls
    const volSlider = document.getElementById('setting_sound_volume');
    const volBadge = document.getElementById('volumeValueBadge');

    if (volSlider && volBadge) {
        volSlider.addEventListener('input', (e) => {
            volBadge.textContent = `${e.target.value}%`;
        });
    }

    document.getElementById('btnTestSound').addEventListener('click', () => {
        const val = parseInt(volSlider.value, 10) || 80;
        playAlertSound(val);
        addLogLine('SoundTest', `Đang phát âm thử nghiệm ở mức ${val}%`, 'info');
    });

    // Render Channel Cards Grid
    function renderChannelsGrid(containerId, channelsObj, categoryPrefix) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        Object.keys(channelsObj).forEach(key => {
            const item = channelsObj[key];
            const card = document.createElement('div');
            card.className = 'channel-card';
            card.setAttribute('data-key', key);

            const isCustom = item.isCustom || categoryPrefix === 'cust';
            const logoHtml = item.logo ? `<img src="${escapeHtml(item.logo)}" class="mode-logo-icon" alt="logo">` : '';

            card.innerHTML = `
                <div class="channel-card-header">
                    <span class="channel-title-text">
                        ${logoHtml}
                        ${isCustom ? `<input type="text" class="channel-title-input" id="${categoryPrefix}_ch_${key}_name" value="${escapeHtml(item.name || 'Custom Server')}" style="padding: 2px 6px; font-size: 12px; width: 140px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: #fff;">` : escapeHtml(item.name || key)}
                    </span>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${isCustom ? `<button class="btn btn-sm btn-danger btn-remove-custom" data-prefix="${categoryPrefix}" data-key="${key}" style="padding: 2px 6px; font-size: 10px;" title="Xóa Server này"><i class="fa-solid fa-trash"></i></button>` : ''}
                        <label class="switch" style="transform: scale(0.85);">
                            <input type="checkbox" id="${categoryPrefix}_ch_${key}_enable" ${item.enabled !== false ? 'checked' : ''}>
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>
                <div class="channel-card-inputs">
                    <div class="mini-input-group">
                        <span class="mini-label"><i class="fa-solid fa-server"></i> Server ID:</span>
                        <input type="text" class="channel-input-sm" id="${categoryPrefix}_ch_${key}_sid" value="${escapeHtml(item.server_id || '')}" placeholder="Server ID...">
                    </div>
                    <div class="mini-input-group">
                        <span class="mini-label"><i class="fa-solid fa-hashtag"></i> Channel ID:</span>
                        <input type="text" class="channel-input-sm" id="${categoryPrefix}_ch_${key}_cid" value="${escapeHtml(item.channel_id || '')}" placeholder="Channel ID...">
                    </div>
                    <div class="mini-input-group">
                        <span class="mini-label"><i class="fa-solid fa-robot"></i> Bot ID:</span>
                        <input type="text" class="channel-input-sm" id="${categoryPrefix}_ch_${key}_bid" value="${escapeHtml(item.bot_id || '')}" placeholder="Bot ID (để trống nếu tự khớp)...">
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

        // Bind Remove buttons
        container.querySelectorAll('.btn-remove-custom').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prefix = btn.getAttribute('data-prefix');
                const k = btn.getAttribute('data-key');
                if (prefix === 'mc') {
                    delete activeMctiersChannels[k];
                    renderChannelsGrid('mctiersChannelsGrid', activeMctiersChannels, 'mc');
                } else if (prefix === 'pvp') {
                    delete activePvptiersChannels[k];
                    renderChannelsGrid('pvptiersChannelsGrid', activePvptiersChannels, 'pvp');
                } else if (prefix === 'cust') {
                    delete activeCustomChannels[k];
                    renderChannelsGrid('customChannelsGrid', activeCustomChannels, 'cust');
                }
                addLogLine('Custom', `Đã xóa Custom Server: ${k}`, 'info');
            });
        });
    }

    // Add Custom Server Action in dedicated CUSTOM SERVERS Tab
    document.getElementById('btnAddCustomServer').addEventListener('click', () => {
        const name = prompt('Nhập tên Server Custom (ví dụ: Custom Tier Server):', '🌐 Custom Server');
        if (!name) return;

        const customKey = `custom_${Date.now()}`;
        activeCustomChannels[customKey] = {
            enabled: true,
            name: name.trim(),
            server_id: "",
            channel_id: "",
            bot_id: "",
            isCustom: true
        };

        renderChannelsGrid('customChannelsGrid', activeCustomChannels, 'cust');
        addLogLine('Custom', `Đã thêm Custom Server mới: '${name}' vào danh sách Custom`, 'success');
    });

    // Start Custom Servers Action
    document.getElementById('btnStartCustom').addEventListener('click', async () => {
        const cfg = gatherConfigFromForm();
        if (!pyApi) return;
        
        const res = await pyApi.start_queue('custom', cfg);
        if (res && res.success) {
            document.getElementById('btnStartCustom').disabled = true;
            document.getElementById('btnStopCustom').disabled = false;
            addLogLine('Custom', '🚀 Đã bắt đầu trực các kênh CUSTOM SERVERS!', 'success');
        }
    });

    // Stop Custom Servers Action
    document.getElementById('btnStopCustom').addEventListener('click', async () => {
        if (!pyApi) return;
        await pyApi.stop_queue('custom');
        document.getElementById('btnStartCustom').disabled = false;
        document.getElementById('btnStopCustom').disabled = true;
    });

    // Mode Selector Pills Event Listeners
    document.querySelectorAll('.mode-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const modeKey = pill.getAttribute('data-mode');
            setMode(modeKey);
        });
    });

    function setMode(modeKey) {
        if (!modeDescriptions[modeKey]) return;
        activeClickMode = modeKey;

        document.querySelectorAll('.mode-pill').forEach(p => {
            if (p.getAttribute('data-mode') === modeKey) {
                p.classList.add('active');
            } else {
                p.classList.remove('active');
            }
        });

        const info = modeDescriptions[modeKey];
        document.getElementById('modeTitle').textContent = info.title;
        document.getElementById('modeDesc').textContent = info.desc;
        document.getElementById('modeHeaderIcon').className = info.icon;

        addLogLine('Mode', `Đã chuyển sang chế độ click: ${info.title.toUpperCase()}`, 'info');
    }

    // Tab Navigation
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`pane-${targetTab}`).classList.add('active');
        });
    });

    // Polling Log Queue
    async function pollLogs() {
        if (!pyApi || !pyApi.get_logs) return;
        try {
            const logs = await pyApi.get_logs();
            if (Array.isArray(logs) && logs.length > 0) {
                logs.forEach(item => {
                    addLogLine(item.sender || 'Engine', item.message, item.level || 'info');
                    if (item.message && item.message.includes("CƯỚP NÚT JOIN QUEUE THÀNH CÔNG")) {
                        const soundEnabled = document.getElementById('setting_sound_alert').checked;
                        if (soundEnabled) {
                            const vol = parseInt(document.getElementById('setting_sound_volume').value, 10) || 80;
                            playAlertSound(vol);
                        }
                    }
                });
            }
        } catch (e) {
            console.error("Poll logs error:", e);
        }
    }

    // Polling Status Queue
    async function pollStatuses() {
        if (!pyApi || !pyApi.get_statuses) return;
        try {
            const statuses = await pyApi.get_statuses();
            if (Array.isArray(statuses) && statuses.length > 0) {
                statuses.forEach(item => {
                    updateCategoryStatus(item.category, item.state, item.extra);
                });
            }
        } catch (e) {
            console.error("Poll statuses error:", e);
        }
    }

    // Logging Utility
    window.addLogLine = function(sender, message, level = 'info') {
        if (!logTerminal) return;

        logLinesCount++;
        logCountBadge.textContent = logLinesCount;

        const timeStr = new Date().toLocaleTimeString('vi-VN');
        const line = document.createElement('div');
        line.className = `log-line ${level.toLowerCase()}`;
        line.setAttribute('data-level', level.toLowerCase());

        line.innerHTML = `
            <span class="log-time">[${timeStr}]</span>
            <span class="log-msg"><strong>[${sender}]</strong> ${escapeHtml(message)}</span>
        `;

        if (activeLogFilter !== 'all' && level.toLowerCase() !== activeLogFilter) {
            line.style.display = 'none';
        }

        logTerminal.appendChild(line);
        logTerminal.scrollTop = logTerminal.scrollHeight;
    };

    function escapeHtml(text) {
        if (!text) return '';
        return text.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    // HWID License Check Function
    async function checkHwidLicense() {
        if (!pyApi || !pyApi.get_hwid_info) return true;
        try {
            const hwidRes = await pyApi.get_hwid_info();
            const lockOverlay = document.getElementById('hwidLockOverlay');
            const keyInput = document.getElementById('hwidKeyInput');

            if (hwidRes && hwidRes.hwid) {
                if (keyInput) keyInput.value = hwidRes.hwid;
            }

            if (hwidRes && !hwidRes.authorized) {
                if (lockOverlay) lockOverlay.classList.remove('hidden');
                addLogLine('License', '🔒 Mã phần cứng (HWID) chưa được kích hoạt bản quyền!', 'error');
                return false;
            } else {
                if (lockOverlay) lockOverlay.classList.add('hidden');
                addLogLine('License', '✅ Xác thực HWID bản quyền thành công.', 'success');
                return true;
            }
        } catch (e) {
            console.error("HWID check error:", e);
            return true;
        }
    }

    // Load Initial Config
    async function loadInitialConfig() {
        if (!pyApi) return;
        try {
            await checkHwidLicense();
            const cfg = await pyApi.get_config();
            currentConfig = cfg || {};
            populateFormFields(currentConfig);

            if (currentConfig.user_token) {
                validateToken(currentConfig.user_token, false);
            }
        } catch (e) {
            addLogLine('Error', 'Khởi tạo cấu hình thất bại: ' + e, 'error');
        }
    }

    // HWID Buttons Action Handlers
    const btnCopyHwid = document.getElementById('btnCopyHwid');
    if (btnCopyHwid) {
        btnCopyHwid.addEventListener('click', () => {
            const hwidVal = document.getElementById('hwidKeyInput').value;
            if (hwidVal) {
                navigator.clipboard.writeText(hwidVal);
                addLogLine('License', `📋 Đã sao chép HWID: ${hwidVal}`, 'success');
                btnCopyHwid.innerHTML = '<i class="fa-solid fa-check"></i> Đã Sao Chép!';
                setTimeout(() => {
                    btnCopyHwid.innerHTML = '<i class="fa-solid fa-copy"></i> Sao Chép HWID';
                }, 2000);
            }
        });
    }

    const btnRecheckHwid = document.getElementById('btnRecheckHwid');
    if (btnRecheckHwid) {
        btnRecheckHwid.addEventListener('click', async () => {
            btnRecheckHwid.disabled = true;
            btnRecheckHwid.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang kiểm tra...';
            await checkHwidLicense();
            btnRecheckHwid.disabled = false;
            btnRecheckHwid.innerHTML = '<i class="fa-solid fa-rotate"></i> Kiểm Tra Lại Kích Hoạt';
        });
    }

    const btnActivateKey = document.getElementById('btnActivateKey');
    if (btnActivateKey) {
        btnActivateKey.addEventListener('click', async () => {
            const keyVal = document.getElementById('licenseKeyInput').value.trim();
            if (!keyVal) {
                alert('Vui lòng nhập mã License Key!');
                return;
            }
            if (!pyApi || !pyApi.activate_license_key) return;

            btnActivateKey.disabled = true;
            btnActivateKey.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';

            try {
                const res = await pyApi.activate_license_key(keyVal);
                if (res && res.success) {
                    alert(res.message);
                    await checkHwidLicense();
                } else {
                    alert(res ? res.message : 'Kích hoạt key thất bại!');
                }
            } catch (e) {
                alert('Lỗi kích hoạt key: ' + e);
            } finally {
                btnActivateKey.disabled = false;
                btnActivateKey.innerHTML = '<i class="fa-solid fa-key"></i> Kích Hoạt';
            }
        });
    }

    // Populate fields from config
    function populateFormFields(cfg) {
        document.getElementById('user_token').value = cfg.user_token || '';
        document.getElementById('webhook_url').value = cfg.webhook_url || '';
        document.getElementById('setting_webhook_enabled').checked = cfg.webhook_enabled ?? true;

        const soundAlert = cfg.global_settings?.sound_alert ?? true;
        const soundVolume = cfg.global_settings?.sound_volume ?? 80;
        const constellation = cfg.global_settings?.constellation ?? true;
        const savedMode = cfg.global_settings?.click_mode || 'turbo';

        setMode(savedMode);

        document.getElementById('setting_sound_alert').checked = soundAlert;
        document.getElementById('setting_sound_volume').value = soundVolume;
        document.getElementById('volumeValueBadge').textContent = `${soundVolume}%`;

        document.getElementById('setting_constellation').checked = constellation;

        if (window.ConstellationEngine) {
            window.ConstellationEngine.toggle(constellation);
        }

        activeMctiersChannels = cfg.mctiers_channels || defaultMctiersChannels;
        activePvptiersChannels = cfg.pvptiers_channels || defaultPvptiersChannels;
        activeCustomChannels = cfg.custom_channels || defaultCustomChannels;

        renderChannelsGrid('mctiersChannelsGrid', activeMctiersChannels, 'mc');
        renderChannelsGrid('pvptiersChannelsGrid', activePvptiersChannels, 'pvp');
        renderChannelsGrid('customChannelsGrid', activeCustomChannels, 'cust');

        if (cfg.mctiers && cfg.mctiers.join_button_labels) {
            document.getElementById('mctiers_join_labels').value = cfg.mctiers.join_button_labels.join(', ');
        }
        if (cfg.pvptiers && cfg.pvptiers.join_button_labels) {
            document.getElementById('pvptiers_join_labels').value = cfg.pvptiers.join_button_labels.join(', ');
        }
        if (cfg.custom && cfg.custom.join_button_labels) {
            document.getElementById('custom_join_labels').value = cfg.custom.join_button_labels.join(', ');
        }
    }

    function gatherChannelsData(containerId, categoryPrefix, currentChannelsMap) {
        const result = {};
        const container = document.getElementById(containerId);
        if (!container) return currentChannelsMap;

        const cards = container.querySelectorAll('.channel-card');
        cards.forEach(card => {
            const key = card.getAttribute('data-key');
            const enableEl = document.getElementById(`${categoryPrefix}_ch_${key}_enable`);
            const nameEl = document.getElementById(`${categoryPrefix}_ch_${key}_name`);
            const sidEl = document.getElementById(`${categoryPrefix}_ch_${key}_sid`);
            const cidEl = document.getElementById(`${categoryPrefix}_ch_${key}_cid`);
            const bidEl = document.getElementById(`${categoryPrefix}_ch_${key}_bid`);

            const existingItem = currentChannelsMap[key] || {};
            const titleName = nameEl ? nameEl.value.trim() : (existingItem.name || key);

            result[key] = {
                enabled: enableEl ? enableEl.checked : true,
                name: titleName,
                server_id: sidEl ? sidEl.value.trim() : existingItem.server_id,
                channel_id: cidEl ? cidEl.value.trim() : existingItem.channel_id,
                bot_id: bidEl ? bidEl.value.trim() : existingItem.bot_id,
                isCustom: existingItem.isCustom || categoryPrefix === 'cust',
                logo: existingItem.logo || ""
            };
        });
        return result;
    }

    function gatherConfigFromForm() {
        const labelsMc = document.getElementById('mctiers_join_labels').value.split(',').map(s => s.trim()).filter(Boolean);
        const labelsPvp = document.getElementById('pvptiers_join_labels').value.split(',').map(s => s.trim()).filter(Boolean);
        const labelsCust = document.getElementById('custom_join_labels').value.split(',').map(s => s.trim()).filter(Boolean);

        const mctiersChannels = gatherChannelsData('mctiersChannelsGrid', 'mc', activeMctiersChannels);
        const pvptiersChannels = gatherChannelsData('pvptiersChannelsGrid', 'pvp', activePvptiersChannels);
        const customChannels = gatherChannelsData('customChannelsGrid', 'cust', activeCustomChannels);

        return {
            user_token: document.getElementById('user_token').value.trim(),
            webhook_url: document.getElementById('webhook_url').value.trim(),
            webhook_enabled: document.getElementById('setting_webhook_enabled').checked,
            global_settings: {
                click_mode: activeClickMode,
                sound_alert: document.getElementById('setting_sound_alert').checked,
                sound_volume: parseInt(document.getElementById('setting_sound_volume').value, 10) || 80,
                constellation: document.getElementById('setting_constellation').checked,
                anti_screenshot: true
            },
            mctiers_channels: mctiersChannels,
            pvptiers_channels: pvptiersChannels,
            custom_channels: customChannels,
            mctiers: {
                name: 'MCTIERS',
                join_button_labels: labelsMc.length ? labelsMc : ['Join Queue', 'Join', 'Queue']
            },
            pvptiers: {
                name: 'PVPTIERS',
                join_button_labels: labelsPvp.length ? labelsPvp : ['Join Queue', 'Join', 'Queue']
            },
            custom: {
                name: 'CUSTOM SERVERS',
                join_button_labels: labelsCust.length ? labelsCust : ['Join Queue', 'Join', 'Queue']
            }
        };
    }

    // Auto-Detect Token Handler
    document.getElementById('btnAutoDetectToken').addEventListener('click', async () => {
        if (!pyApi || !pyApi.auto_detect_token) return;
        
        const btn = document.getElementById('btnAutoDetectToken');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tìm...';

        try {
            const res = await pyApi.auto_detect_token();
            if (res && res.success) {
                document.getElementById('user_token').value = res.token;
                document.getElementById('statusUsernameText').innerHTML = `Logged in (<span class="user-at-name">@${escapeHtml(res.username)}</span>)`;
                document.getElementById('userAvatarImg').src = res.avatar_url;
                addLogLine('AutoDetect', `Thành công! Đã tự động lấy Token của @${res.username}`, 'success');
            } else {
                addLogLine('AutoDetect', res ? res.message : 'Không tìm thấy Token', 'warning');
            }
        } catch (e) {
            addLogLine('AutoDetect', 'Lỗi quét Token: ' + e, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Auto-Detect Token';
        }
    });

    // Save Config Action
    document.getElementById('btnSaveConfig').addEventListener('click', async () => {
        const newCfg = gatherConfigFromForm();
        if (!pyApi) {
            alert('Python Backend chưa kết nối!');
            return;
        }
        const success = await pyApi.save_config(newCfg);
        if (success) {
            currentConfig = newCfg;
            addLogLine('Config', 'Đã lưu cài đặt vào config.json thành công!', 'success');
        } else {
            addLogLine('Config', 'Lưu cài đặt thất bại!', 'error');
        }
    });

    // Test Webhook Action
    document.getElementById('btnTestWebhook').addEventListener('click', async () => {
        const webhookUrl = document.getElementById('webhook_url').value.trim();
        if (!webhookUrl) {
            alert('Vui lòng dán Webhook URL trước khi Test!');
            return;
        }
        if (!pyApi || !pyApi.test_webhook) return;
        const res = await pyApi.test_webhook(webhookUrl);
        if (res && res.success) {
            addLogLine('Webhook', res.message, 'success');
        } else {
            addLogLine('Webhook', res ? res.message : 'Lỗi gửi Webhook', 'error');
        }
    });

    async function validateToken(token, showToast = true) {
        if (!pyApi || !token) {
            document.getElementById('statusUsernameText').textContent = 'Chưa xác thực Token';
            document.getElementById('userAvatarImg').src = 'https://cdn.discordapp.com/embed/avatars/0.png';
            return;
        }

        const usernameTextEl = document.getElementById('statusUsernameText');
        const avatarImg = document.getElementById('userAvatarImg');
        usernameTextEl.textContent = 'Đang kiểm tra...';
        
        try {
            const res = await pyApi.validate_token(token);
            if (res && res.valid) {
                if (res.username) {
                    usernameTextEl.innerHTML = `Logged in (<span class="user-at-name">@${escapeHtml(res.username)}</span>)`;
                }
                if (res.avatar_url) avatarImg.src = res.avatar_url;
                if (showToast) addLogLine('Discord', res.message, 'success');
            } else {
                usernameTextEl.textContent = 'Chưa xác thực Token';
                avatarImg.src = 'https://cdn.discordapp.com/embed/avatars/0.png';
                if (showToast) addLogLine('Discord', res ? res.message : 'Lỗi token', 'error');
            }
        } catch (e) {
            usernameTextEl.textContent = 'Chưa xác thực Token';
            avatarImg.src = 'https://cdn.discordapp.com/embed/avatars/0.png';
            if (showToast) addLogLine('Discord', 'Lỗi kiểm tra token: ' + e, 'error');
        }
    }

    document.getElementById('btnValidateToken').addEventListener('click', () => {
        const token = document.getElementById('user_token').value.trim();
        validateToken(token, true);
    });

    // Token Visibility Toggle
    document.getElementById('btnToggleTokenVisibility').addEventListener('click', () => {
        const tokenInput = document.getElementById('user_token');
        const eyeIcon = document.getElementById('tokenEyeIcon');
        if (tokenInput.type === 'password') {
            tokenInput.type = 'text';
            eyeIcon.className = 'fa-solid fa-eye-slash';
        } else {
            tokenInput.type = 'password';
            eyeIcon.className = 'fa-solid fa-eye';
        }
    });

    // Constellation Toggle Handler
    document.getElementById('setting_constellation').addEventListener('change', (e) => {
        if (window.ConstellationEngine) {
            window.ConstellationEngine.toggle(e.target.checked);
        }
    });

    // Start / Stop Handlers for MCTIERS
    document.getElementById('btnStartMctiers').addEventListener('click', async () => {
        const cfg = gatherConfigFromForm();
        if (!pyApi) return;
        const res = await pyApi.start_queue('mctiers', cfg);
        if (res && res.success) {
            document.getElementById('btnStartMctiers').disabled = true;
            document.getElementById('btnStopMctiers').disabled = false;
        }
    });

    document.getElementById('btnStopMctiers').addEventListener('click', async () => {
        if (!pyApi) return;
        await pyApi.stop_queue('mctiers');
        document.getElementById('btnStartMctiers').disabled = false;
        document.getElementById('btnStopMctiers').disabled = true;
    });

    // Start / Stop Handlers for PVPTIERS
    document.getElementById('btnStartPvptiers').addEventListener('click', async () => {
        const cfg = gatherConfigFromForm();
        if (!pyApi) return;
        const res = await pyApi.start_queue('pvptiers', cfg);
        if (res && res.success) {
            document.getElementById('btnStartPvptiers').disabled = true;
            document.getElementById('btnStopPvptiers').disabled = false;
        }
    });

    document.getElementById('btnStopPvptiers').addEventListener('click', async () => {
        if (!pyApi) return;
        await pyApi.stop_queue('pvptiers');
        document.getElementById('btnStartPvptiers').disabled = false;
        document.getElementById('btnStopPvptiers').disabled = true;
    });

    // Stop All
    document.getElementById('btnStopAll').addEventListener('click', async () => {
        if (!pyApi) return;
        await pyApi.stop_all();
        document.getElementById('btnStartMctiers').disabled = false;
        document.getElementById('btnStopMctiers').disabled = true;
        document.getElementById('btnStartPvptiers').disabled = false;
        document.getElementById('btnStopPvptiers').disabled = true;
        document.getElementById('btnStartCustom').disabled = false;
        document.getElementById('btnStopCustom').disabled = true;
    });

    // Log terminal controls
    document.getElementById('btnClearLogs').addEventListener('click', () => {
        logTerminal.innerHTML = '';
        logLinesCount = 0;
        logCountBadge.textContent = 0;
    });

    document.querySelectorAll('.log-controls .btn-icon').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.log-controls .btn-icon').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeLogFilter = btn.getAttribute('data-filter');

            document.querySelectorAll('#logTerminal .log-line').forEach(line => {
                const lvl = line.getAttribute('data-level');
                if (activeLogFilter === 'all' || lvl === activeLogFilter) {
                    line.style.display = 'flex';
                } else {
                    line.style.display = 'none';
                }
            });
        });
    });

    // Status Updates Handler
    function updateCategoryStatus(category, state, extra) {
        const badge = document.getElementById(`${category}Badge`);
        const ringContainer = document.getElementById('avatarRingContainer');
        const statusAction = document.getElementById('statusAction');
        const statusTarget = document.getElementById('statusTarget');

        if (badge) {
            badge.className = `tab-badge ${state}`;
            badge.textContent = state.toUpperCase();
        }

        if (state === 'watching' || state === 'active') {
            ringContainer.className = 'avatar-ring-container idle';
            statusAction.textContent = 'WATCHING';
            const targetName = (extra && extra.target) ? extra.target : category.toUpperCase();
            statusTarget.textContent = targetName;
        } else if (state === 'queued') {
            ringContainer.className = 'avatar-ring-container active';
            statusAction.textContent = 'QUEUED';
            const targetName = (extra && extra.target) ? extra.target : category.toUpperCase();
            statusTarget.textContent = targetName;

            const soundEnabled = document.getElementById('setting_sound_alert').checked;
            if (soundEnabled) {
                const vol = parseInt(document.getElementById('setting_sound_volume').value, 10) || 80;
                playAlertSound(vol);
            }
        } else {
            ringContainer.className = 'avatar-ring-container idle';
            statusAction.textContent = 'WATCHING';
            statusTarget.textContent = '';
        }
    }
})();
