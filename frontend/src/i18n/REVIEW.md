# Bangla strings: needs native review

Every Bangla string in `bn.json` is listed here (workflow rule 7). Read this file aloud and fix awkward wording.
A test (`src/test/i18n.test.ts`) fails if a key is in `bn.json` but missing from this table.
Status column: change to `reviewed` once a native speaker has read it. Regenerate with `npm run gen:review`
(a changed string goes back to "needs native review").

Points to look at first: the watermark and disclaimer, the six verdict summaries, all `rules.*` text, the product
name in `app.name`, and anything that uses legal words (khas, vested, namjari, mutation).

| Key | Bangla | Status |
|---|---|---|
| `app.name` | ল্যান্ডচেক | needs native review |
| `app.title` | ল্যান্ডচেক: কেনার আগে যাচাই করুন | needs native review |
| `language.switch` | English | needs native review |
| `layout.skipToContent` | মূল অংশে যান | needs native review |
| `layout.verifyLink` | প্রতিবেদন যাচাই | needs native review |
| `footer.disclaimer` | এই প্রতিবেদন শুধু পরামর্শমূলক এবং কেবল উল্লিখিত উৎস ও তারিখের তথ্যের ওপর ভিত্তি করে তৈরি। এটি আইনি মতামত বা মালিকানার নিশ্চয়তা নয়। টাকা দেওয়ার আগে আইনজীবীর পরামর্শ নিন এবং জমি সরেজমিনে দেখুন। | needs native review |
| `footer.watermark` | কাল্পনিক তথ্য — প্রকৃত ভূমি রেকর্ড নয় (SYNTHETIC — NOT A REAL LAND RECORD) | needs native review |
| `footer.watermarkShort` | কাল্পনিক | needs native review |
| `common.loading` | লোড হচ্ছে… | needs native review |
| `common.retry` | আবার চেষ্টা করুন | needs native review |
| `common.back` | ফিরে যান | needs native review |
| `common.print` | ছাপুন বা পিডিএফ করুন | needs native review |
| `common.copy` | কপি করুন | needs native review |
| `common.copied` | কপি হয়েছে | needs native review |
| `common.optional` | (ঐচ্ছিক) | needs native review |
| `common.required` | আবশ্যক | needs native review |
| `common.select` | বেছে নিন… | needs native review |
| `common.notAvailable` | পাওয়া যায়নি | needs native review |
| `common.none` | নেই | needs native review |
| `common.done` | সম্পন্ন | needs native review |
| `common.mockBanner` | ডেমো তথ্য: এই পাতায় সংরক্ষিত নমুনা উত্তর দেখানো হচ্ছে, সরাসরি সেবা নয়। | needs native review |
| `errors.NETWORK` | সেবার সাথে সংযোগ করা যায়নি। ইন্টারনেট দেখে আবার চেষ্টা করুন। | needs native review |
| `errors.TIMEOUT` | সেবা উত্তর দিতে অনেক সময় নিচ্ছে। আবার চেষ্টা করুন। | needs native review |
| `errors.VALIDATION_ERROR` | কিছু তথ্য সঠিক নয়। ফর্মটি আবার দেখুন। | needs native review |
| `errors.NOT_FOUND` | এটি খুঁজে পাওয়া যায়নি। | needs native review |
| `errors.RATE_LIMITED` | অনেক বেশি অনুরোধ হয়েছে। এক মিনিট অপেক্ষা করে আবার চেষ্টা করুন। | needs native review |
| `errors.DEMO_DISABLED` | এই সার্ভারে ডেমো কনসোল বন্ধ আছে। | needs native review |
| `errors.NOT_IMPLEMENTED` | এই ডেমো কাজটি এখনো চালু হয়নি। | needs native review |
| `errors.INTERNAL` | আমাদের দিকে একটি সমস্যা হয়েছে। আবার চেষ্টা করুন। | needs native review |
| `errors.BAD_RESPONSE` | সেবা এমন উত্তর দিয়েছে যা পড়া যায়নি। | needs native review |
| `errors.MOCK_MISSING` | এই তথ্যের জন্য কোনো নমুনা উত্তর নেই। নমুনা জমির একটি বেছে নিন। | needs native review |
| `errors.UNKNOWN` | অপ্রত্যাশিত একটি সমস্যা হয়েছে। | needs native review |
| `pages.home.title` | হোম | needs native review |
| `pages.home.promise` | কেনার আগে যাচাই করুন | needs native review |
| `pages.home.lead` | জমির তথ্য আর বিক্রেতার নাম দিন। আমরা ছয়টি উৎস দেখে জানাব কী পেয়েছি, কী যাচাই করতে পারিনি, আর পরবর্তী ধাপে কী জিজ্ঞেস করবেন। | needs native review |
| `pages.home.start` | জমি যাচাই করুন | needs native review |
| `pages.home.verifyCta` | প্রতিবেদন যাচাই করুন | needs native review |
| `pages.home.howTitle` | যেভাবে কাজ করে | needs native review |
| `pages.home.step1` | জমি আর বিক্রেতার তথ্য দিন। | needs native review |
| `pages.home.step2` | আমরা উৎসগুলো যাচাই করি। | needs native review |
| `pages.home.step3` | ফলাফল পড়ুন, তারপর প্রতিবেদন ছাপুন বা শেয়ার করুন। | needs native review |
| `pages.home.checksTitle` | আমরা যা দেখি | needs native review |
| `pages.home.samplesTitle` | একটি নমুনা জমি চেষ্টা করুন | needs native review |
| `pages.home.samplesHelp` | এই জমিগুলো ডেমোর জন্য বানানো। | needs native review |
| `pages.home.syntheticNote` | এই প্রোটোটাইপের সব তথ্য কাল্পনিক। | needs native review |
| `pages.home.demoLink` | ডেমো কনসোল (উপস্থাপনার জন্য) | needs native review |
| `pages.check.title` | জমির তথ্য দিন | needs native review |
| `pages.check.intro` | বাংলা বা ইংরেজি, দুই ধরনের অঙ্কই চলবে। | needs native review |
| `pages.check.sample` | নমুনা জমি দিয়ে ফর্ম পূরণ করুন | needs native review |
| `pages.check.plotTitle` | জমি | needs native review |
| `pages.check.sellerTitle` | বিক্রেতা | needs native review |
| `pages.check.district` | জেলা | needs native review |
| `pages.check.upazila` | উপজেলা | needs native review |
| `pages.check.mouza` | মৌজা | needs native review |
| `pages.check.mouzaOption` | {{name}} (জেএল {{jl}}) | needs native review |
| `pages.check.survey` | জরিপের ধরন | needs native review |
| `pages.check.surveyUnknown` | নিশ্চিত নই | needs native review |
| `pages.check.khatian` | খতিয়ান নম্বর | needs native review |
| `pages.check.dag` | দাগ নম্বর | needs native review |
| `pages.check.sellerName` | বিক্রেতার নাম | needs native review |
| `pages.check.father` | পিতা বা স্বামীর নাম | needs native review |
| `pages.check.fatherHelp` | একই নামের মানুষদের আলাদা করতে সাহায্য করে। | needs native review |
| `pages.check.consentBank` | ব্যাংক বন্ধকও যাচাই করুন | needs native review |
| `pages.check.consentHelp` | এর জন্য আপনার সম্মতি লাগবে। সম্মতি না দিলে ব্যাংকের রেকর্ড দেখা হবে না এবং ফলাফলে তা জানানো হবে। | needs native review |
| `pages.check.submit` | এই জমি যাচাই করুন | needs native review |
| `pages.check.fieldRequired` | এই ঘরটি পূরণ করা আবশ্যক। | needs native review |
| `pages.check.fixErrors` | চিহ্নিত ঘরগুলো ঠিক করুন। | needs native review |
| `pages.check.loadFailed` | জায়গার তালিকা আনা যায়নি। | needs native review |
| `pages.checking.title` | উৎসগুলো যাচাই করা হচ্ছে… | needs native review |
| `pages.checking.subtitle` | সাধারণত কয়েক সেকেন্ড লাগে। পাতাটি খোলা রাখুন। | needs native review |
| `pages.checking.listTitle` | আমরা জানতে চাইছি | needs native review |
| `pages.checking.failedTitle` | যাচাই শেষ হয়নি | needs native review |
| `pages.checking.backToForm` | ফর্মে ফিরে যান | needs native review |
| `pages.result.title` | ফলাফল | needs native review |
| `pages.result.loadFailed` | এই প্রতিবেদন আনা যায়নি। | needs native review |
| `pages.result.plotTitle` | জমি | needs native review |
| `pages.result.plotLine` | {{mouza}}, {{upazila}}, {{district}} | needs native review |
| `pages.result.khatianDag` | খতিয়ান {{khatian}}, দাগ {{dag}} | needs native review |
| `pages.result.area` | {{area}} শতক | needs native review |
| `pages.result.sellerTitle` | বিক্রেতা | needs native review |
| `pages.result.nameMatch` | নামের মিল: {{tier}} | needs native review |
| `pages.result.holders` | রেকর্ডে বর্তমান মালিক: {{count}} জন | needs native review |
| `pages.result.issued` | প্রদানের সময় | needs native review |
| `pages.result.validUntil` | মেয়াদ | needs native review |
| `pages.result.reportId` | প্রতিবেদন নম্বর | needs native review |
| `pages.result.shortCode` | যাচাইকরণ কোড | needs native review |
| `pages.result.noReportId` | ইস্যু করা হয়নি (রেকর্ডের ইতিহাস পরীক্ষায় ব্যর্থ) | needs native review |
| `pages.result.coverageTitle` | আমরা যা যাচাই করতে পেরেছি | needs native review |
| `pages.result.findingsTitle` | আমরা যা পেয়েছি | needs native review |
| `pages.result.noFindings` | কোনো পর্যবেক্ষণ নেই। | needs native review |
| `pages.result.notCheckedTitle` | আমরা যা যাচাই করিনি | needs native review |
| `pages.result.notCheckedHelp` | এই প্রতিবেদনে এগুলো নেই। নিজে বা আইনজীবীর সাহায্যে যাচাই করুন। | needs native review |
| `pages.result.sourcesTitle` | উৎস | needs native review |
| `pages.result.asOf` | {{date}} তারিখ পর্যন্ত | needs native review |
| `pages.result.recordCount` | {{count}}টি রেকর্ড | needs native review |
| `pages.result.timelineTitle` | মালিকানার সময়রেখা | needs native review |
| `pages.result.noTimeline` | মালিকানার কোনো ইতিহাস পাওয়া যায়নি। | needs native review |
| `pages.result.timelineMove` | {{from}} → {{to}} | needs native review |
| `pages.result.flagged` | চিহ্নিত করেছে {{rules}} | needs native review |
| `pages.result.ledgerTitle` | রেকর্ডের ইতিহাস | needs native review |
| `pages.result.ledgerOk` | অক্ষত। ইতিহাসে {{height}}টি এন্ট্রি আছে এবং তা স্বাক্ষরিত চেকপয়েন্টের সাথে মেলে। | needs native review |
| `pages.result.ledgerBroken` | অখণ্ডতা পরীক্ষায় ব্যর্থ: {{reason}}। | needs native review |
| `pages.result.printCta` | ছাপুন বা পিডিএফ করুন | needs native review |
| `pages.result.verifyCta` | এই প্রতিবেদন যাচাই করুন | needs native review |
| `pages.result.newCheck` | আরেকটি জমি যাচাই করুন | needs native review |
| `pages.result.qrTitle` | যাচাই করতে স্ক্যান করুন | needs native review |
| `pages.result.qrAlt` | এই প্রতিবেদনের যাচাই পাতা খোলার কিউআর কোড | needs native review |
| `pages.result.verdictWord` | সিদ্ধান্ত | needs native review |
| `pages.verify.title` | প্রতিবেদন যাচাই করুন | needs native review |
| `pages.verify.lead` | প্রতিবেদনে ছাপা ৮ অক্ষরের কোডটি দিন, অথবা কিউআর কোড স্ক্যান করুন। আমরা স্বাক্ষর ও রেকর্ডের ইতিহাস যাচাই করব। | needs native review |
| `pages.verify.codeLabel` | যাচাইকরণ কোড | needs native review |
| `pages.verify.codePlaceholder` | যেমন K7M2-9QXA | needs native review |
| `pages.verify.codeHelp` | অক্ষর ও অঙ্ক, ড্যাশ থাকলেও চলবে না থাকলেও। | needs native review |
| `pages.verify.submit` | যাচাই করুন | needs native review |
| `pages.verify.checking` | যাচাই চলছে… | needs native review |
| `pages.verify.fromLink` | আপনার খোলা লিংকের প্রতিবেদন যাচাই করা হচ্ছে… | needs native review |
| `pages.verify.reportTitle` | প্রতিবেদনের বিবরণ | needs native review |
| `pages.verify.verdictAtIssue` | ইস্যুর সময়ের সিদ্ধান্ত: {{verdict}} | needs native review |
| `pages.verify.signatureValid` | স্বাক্ষর বৈধ। | needs native review |
| `pages.verify.signatureInvalid` | স্বাক্ষর বৈধ নয়। | needs native review |
| `pages.verify.browserValid` | আপনার ব্রাউজার নিজেই স্বাক্ষর যাচাই করেছে: বৈধ। | needs native review |
| `pages.verify.browserInvalid` | আপনার ব্রাউজার নিজেই স্বাক্ষর যাচাই করেছে: বৈধ নয়। | needs native review |
| `pages.verify.diffTitle` | প্রতিবেদনের পরে নতুন যা যোগ হয়েছে | needs native review |
| `pages.verify.diffItem` | {{date}} তারিখে {{kind}} ({{ref}}) | needs native review |
| `pages.verify.ledgerOk` | রেকর্ডের ইতিহাস অক্ষত আছে। | needs native review |
| `pages.verify.ledgerBroken` | রেকর্ডের ইতিহাস পরীক্ষায় ব্যর্থ: {{reason}}। | needs native review |
| `pages.verify.checkedAt` | যাচাইয়ের সময় {{date}} | needs native review |
| `pages.verify.newCheck` | নতুন করে যাচাই করুন | needs native review |
| `pages.verify.states.GENUINE_CURRENT.title` | আসল ও হালনাগাদ | needs native review |
| `pages.verify.states.GENUINE_CURRENT.body` | এই প্রতিবেদন এই সেবা থেকেই দেওয়া, অপরিবর্তিত, এবং এরপর নতুন কিছু নথিভুক্ত হয়নি। | needs native review |
| `pages.verify.states.GENUINE_EXPIRED.title` | আসল কিন্তু মেয়াদোত্তীর্ণ | needs native review |
| `pages.verify.states.GENUINE_EXPIRED.body` | এই প্রতিবেদন আমাদের এবং অপরিবর্তিত, কিন্তু মেয়াদ পেরিয়ে গেছে। নতুন করে যাচাই করুন। | needs native review |
| `pages.verify.states.GENUINE_SUPERSEDED.title` | আসল কিন্তু পুরোনো | needs native review |
| `pages.verify.states.GENUINE_SUPERSEDED.body` | এই প্রতিবেদন আমাদের এবং অপরিবর্তিত, কিন্তু এটি দেওয়ার পরে নতুন রেকর্ড যোগ হয়েছে। নতুন করে যাচাই করুন। | needs native review |
| `pages.verify.states.TAMPERED.title` | আসল নয় | needs native review |
| `pages.verify.states.TAMPERED.body` | স্বাক্ষর মেলেনি। প্রতিবেদনটি বদলানো হয়েছে অথবা আমাদের কাছ থেকে আসেনি। এর ওপর ভরসা করবেন না। | needs native review |
| `pages.verify.states.INTEGRITY_ALERT.title` | রেকর্ডের ইতিহাস বদলানো হয়েছে | needs native review |
| `pages.verify.states.INTEGRITY_ALERT.body` | এই প্রতিবেদনের পেছনের রেকর্ডের ইতিহাস পরীক্ষায় ব্যর্থ হয়েছে। এর ওপর ভরসা করবেন না। | needs native review |
| `pages.verify.states.UNKNOWN.title` | প্রতিবেদন পাওয়া যায়নি | needs native review |
| `pages.verify.states.UNKNOWN.body` | এই কোডের কোনো প্রতিবেদন আমাদের কাছে নেই। কোডটি দেখে আবার চেষ্টা করুন। | needs native review |
| `pages.print.title` | ছাপার প্রতিবেদন | needs native review |
| `pages.print.verifyAt` | এই প্রতিবেদন যাচাই করুন: {{url}} | needs native review |
| `pages.print.back` | ফলাফলে ফিরে যান | needs native review |
| `pages.print.hint` | কপি রাখতে ব্রাউজারের প্রিন্ট ডায়ালগে "Save as PDF" বেছে নিন। | needs native review |
| `pages.demo.title` | ডেমো কনসোল | needs native review |
| `pages.demo.intro` | শুধু উপস্থাপনার জন্য। এই বোতামগুলো ডেমোর তথ্য বদলায়। | needs native review |
| `pages.demo.plot` | জমি | needs native review |
| `pages.demo.ledgerTitle` | এই জমির রেকর্ডের ইতিহাস | needs native review |
| `pages.demo.statusOk` | অক্ষত | needs native review |
| `pages.demo.statusBroken` | ভাঙা | needs native review |
| `pages.demo.entryOk` | ঠিক | needs native review |
| `pages.demo.entryBroken` | ভাঙা | needs native review |
| `pages.demo.colSeq` | নং | needs native review |
| `pages.demo.colSource` | উৎস | needs native review |
| `pages.demo.colRecord` | রেকর্ড | needs native review |
| `pages.demo.colStatus` | অবস্থা | needs native review |
| `pages.demo.checkpointValid` | স্বাক্ষরিত চেকপয়েন্ট: বৈধ | needs native review |
| `pages.demo.checkpointInvalid` | স্বাক্ষরিত চেকপয়েন্ট: বৈধ নয় | needs native review |
| `pages.demo.noCheckpoint` | কোনো স্বাক্ষরিত চেকপয়েন্ট নেই | needs native review |
| `pages.demo.tamperTitle` | রেকর্ডে ছেড়াফাঁড়া করুন | needs native review |
| `pages.demo.addTitle` | একটি বৈধ হালনাগাদ যোগ করুন | needs native review |
| `pages.demo.resetTitle` | নতুন করে শুরু | needs native review |
| `pages.demo.reset` | ডেমোর তথ্য আগের অবস্থায় ফেরান | needs native review |
| `pages.demo.clockTitle` | ঘড়ি এগিয়ে দিন | needs native review |
| `pages.demo.clockDays` | কত দিন এগিয়ে | needs native review |
| `pages.demo.clockApply` | প্রয়োগ করুন | needs native review |
| `pages.demo.issueTitle` | ইস্যু ও যাচাই | needs native review |
| `pages.demo.issue` | এই জমির প্রতিবেদন ইস্যু করুন | needs native review |
| `pages.demo.lastReport` | সর্বশেষ প্রতিবেদন: {{code}} ({{verdict}}) | needs native review |
| `pages.demo.verifyLast` | সর্বশেষ প্রতিবেদন যাচাই করুন | needs native review |
| `pages.demo.working` | কাজ চলছে… | needs native review |
| `pages.demo.disabled` | এই সার্ভারে ডেমো কনসোল বন্ধ আছে। | needs native review |
| `pages.demo.scriptTitle` | ডেমো স্ক্রিপ্ট: ছেড়াফাঁড়া বনাম বৈধ হালনাগাদ | needs native review |
| `pages.demo.script1` | P-001-এর প্রতিবেদন ইস্যু করুন (সবুজ)। | needs native review |
| `pages.demo.script2` | একটি রেকর্ড বদলান, তারপর P-001 আবার যাচাই করুন: অখণ্ডতার সতর্কতা। | needs native review |
| `pages.demo.script3` | রিসেট করুন, একটি বৈধ বন্ধক যোগ করুন, প্রথম প্রতিবেদন যাচাই করুন: আসল কিন্তু পুরোনো। | needs native review |
| `pages.demo.tamper.edit_field` | একটি ঘর বদলান | needs native review |
| `pages.demo.tamper.edit_and_rehash` | বদলে ফিঙ্গারপ্রিন্টও নতুন করে গণনা করুন | needs native review |
| `pages.demo.tamper.delete_entry` | একটি এন্ট্রি মুছুন | needs native review |
| `pages.demo.tamper.swap_signature` | স্বাক্ষর বদলে দিন | needs native review |
| `pages.demo.tamper.reorder` | এন্ট্রির ক্রম বদলান | needs native review |
| `pages.demo.tamper.replace_entry` | একটি এন্ট্রি প্রতিস্থাপন করুন | needs native review |
| `pages.demo.tamper.replay_checkpoint` | পুরোনো চেকপয়েন্ট ফিরিয়ে আনুন | needs native review |
| `pages.demo.add.new_mortgage` | নতুন বন্ধক | needs native review |
| `pages.demo.add.new_mutation_pending` | নতুন অপেক্ষমাণ নামজারি | needs native review |
| `pages.notFound.title` | পাতাটি পাওয়া যায়নি | needs native review |
| `pages.notFound.body` | আপনি যে পাতাটি খুলেছেন তা নেই। | needs native review |
| `pages.notFound.home` | হোম পাতায় যান | needs native review |
| `questions.Q1` | বিক্রেতাকে কি মালিক বলে দেখা যাচ্ছে? | needs native review |
| `questions.Q2` | মালিকানার ধারাবাহিকতা কি মিলছে? | needs native review |
| `questions.Q3` | কোনো মামলা বা অপেক্ষমাণ নামজারি আছে কি? | needs native review |
| `questions.Q4` | জমিটি কি খাস বা অর্পিত সম্পত্তির তালিকায় আছে? | needs native review |
| `questions.Q5` | বন্ধক বা একই জমির দ্বৈত বিক্রির চিহ্ন আছে কি? | needs native review |
| `questions.Q6` | রেকর্ডের ইতিহাস কি অক্ষত আছে? | needs native review |
| `coverage.COVERED` | যাচাই হয়েছে | needs native review |
| `coverage.PARTIAL` | আংশিক যাচাই | needs native review |
| `coverage.NOT_COVERED` | যাচাই হয়নি | needs native review |
| `survey.CS` | সিএস (ক্যাডাস্ট্রাল জরিপ) | needs native review |
| `survey.SA` | এসএ (রাষ্ট্রীয় অধিগ্রহণ জরিপ) | needs native review |
| `survey.RS` | আরএস (সংশোধনী জরিপ) | needs native review |
| `survey.BS` | বিএস (বাংলাদেশ জরিপ) | needs native review |
| `surveyShort.CS` | সিএস জরিপ | needs native review |
| `surveyShort.SA` | এসএ জরিপ | needs native review |
| `surveyShort.RS` | আরএস জরিপ | needs native review |
| `surveyShort.BS` | বিএস জরিপ | needs native review |
| `sources.land_records` | জমির রেকর্ড (খতিয়ান) | needs native review |
| `sources.registry` | দলিল নিবন্ধন | needs native review |
| `sources.mutation` | নামজারি | needs native review |
| `sources.court` | আদালতের মামলা | needs native review |
| `sources.khas` | খাস ও অর্পিত তালিকা | needs native review |
| `sources.bank` | ব্যাংক বন্ধক | needs native review |
| `sourceStatus.OK` | উত্তর পাওয়া গেছে | needs native review |
| `sourceStatus.NO_RECORD` | কোনো রেকর্ড নেই | needs native review |
| `sourceStatus.PARTIAL` | আংশিক উত্তর | needs native review |
| `sourceStatus.STALE` | পুরোনো তথ্য | needs native review |
| `sourceStatus.UNAVAILABLE` | পাওয়া যায়নি | needs native review |
| `sourceStatus.ERROR` | ত্রুটি | needs native review |
| `maturity.label` | তথ্যের স্তর {{level}} | needs native review |
| `linkage.EXACT` | দাগ নম্বরে মিলেছে | needs native review |
| `linkage.TEXT_MATCH` | লেখার মিলে পাওয়া | needs native review |
| `linkage.PARTY_NAME_ONLY` | শুধু নাম ধরে খোঁজা | needs native review |
| `reasons.consent_required` | সম্মতি দেওয়া হয়নি | needs native review |
| `reasons.timeout` | সময় শেষ হয়ে গেছে | needs native review |
| `reasons.outage` | সেবা বন্ধ | needs native review |
| `reasons.stale` | তথ্য অনেক পুরোনো | needs native review |
| `reasons.not_digitised` | ডিজিটাল করা হয়নি | needs native review |
| `ledgerReason.hash_mismatch` | একটি রেকর্ড আর তার ফিঙ্গারপ্রিন্টের সাথে মেলে না | needs native review |
| `ledgerReason.link_broken` | এন্ট্রির শিকল ভেঙে গেছে | needs native review |
| `ledgerReason.checkpoint_mismatch` | ইতিহাস আর স্বাক্ষরিত চেকপয়েন্টের সাথে মেলে না | needs native review |
| `ledgerReason.signature_invalid` | চেকপয়েন্টের স্বাক্ষর অবৈধ | needs native review |
| `ledgerReason.height_mismatch` | প্রতিবেদন যে এন্ট্রির ওপর নির্ভর করেছিল তা নেই | needs native review |
| `events.SURVEY_ENTRY` | জরিপে এন্ট্রি | needs native review |
| `events.SALE` | বিক্রয় | needs native review |
| `events.GIFT` | হেবা বা দান | needs native review |
| `events.INHERITANCE` | উত্তরাধিকার | needs native review |
| `events.PARTITION` | বণ্টন | needs native review |
| `events.COURT_DECREE` | আদালতের ডিক্রি | needs native review |
| `events.ACQUISITION` | সরকারি অধিগ্রহণ | needs native review |
| `events.MORTGAGE` | বন্ধক | needs native review |
| `events.MORTGAGE_RELEASE` | বন্ধক মুক্তি | needs native review |
| `events.LT_NOTICE` | ভূমি উন্নয়ন কর নোটিশ | needs native review |
| `events.MUTATION_PENDING` | নামজারি অপেক্ষমাণ | needs native review |
| `events.MUTATION_APPLIED` | নামজারি কার্যকর | needs native review |
| `severity.INTEGRITY` | রেকর্ডের অখণ্ডতা | needs native review |
| `severity.CRITICAL` | গুরুতর | needs native review |
| `severity.HIGH` | উচ্চ | needs native review |
| `severity.MEDIUM` | মাঝারি | needs native review |
| `severity.INFO` | তথ্যের জন্য | needs native review |
| `severity.COVERAGE` | যাচাইয়ের ঘাটতি | needs native review |
| `confidence.HIGH` | উচ্চ নিশ্চয়তা | needs native review |
| `confidence.MEDIUM` | মাঝারি নিশ্চয়তা | needs native review |
| `confidence.LOW` | কম নিশ্চয়তা | needs native review |
| `matchTier.STRONG` | জোরালো | needs native review |
| `matchTier.PROBABLE` | সম্ভাব্য | needs native review |
| `matchTier.WEAK` | দুর্বল | needs native review |
| `matchTier.NONE` | মিল নেই | needs native review |
| `matchTier.NOT_RUN` | চালানো হয়নি | needs native review |
| `verdict.GREEN.label` | কোনো লাল সংকেত পাওয়া যায়নি | needs native review |
| `verdict.GREEN.summary` | আমরা যেসব উৎস দেখেছি তাতে কোনো লাল সংকেত পাওয়া যায়নি। এটি কোনো নিশ্চয়তা নয়। | needs native review |
| `verdict.GREY.label` | যথেষ্ট যাচাই করা যায়নি | needs native review |
| `verdict.GREY.summary` | বলার মতো যথেষ্ট উৎস যাচাই করা যায়নি। এটিকে পরিষ্কার ফলাফল ভাববেন না। | needs native review |
| `verdict.AMBER.label` | আরও খুঁটিয়ে দেখা দরকার | needs native review |
| `verdict.AMBER.summary` | টাকা দেওয়ার আগে যাচাই করার মতো কিছু বিষয় পাওয়া গেছে। | needs native review |
| `verdict.RED.label` | গুরুতর সমস্যা পাওয়া গেছে | needs native review |
| `verdict.RED.summary` | গুরুতর একটি সমস্যা পাওয়া গেছে। আইনজীবী না দেখা পর্যন্ত টাকা দেবেন না। | needs native review |
| `verdict.INTEGRITY_ALERT.label` | রেকর্ড বদলানো হতে পারে | needs native review |
| `verdict.INTEGRITY_ALERT.summary` | রেকর্ডের ইতিহাস অখণ্ডতা পরীক্ষায় ব্যর্থ হয়েছে। এই ফলাফলের ওপর ভরসা করবেন না। | needs native review |
| `rules.R-OWN-01.title` | বিক্রেতার নাম রেকর্ডের সাথে মেলে না | needs native review |
| `rules.R-OWN-01.explain` | আপনার দেওয়া নাম জমির রেকর্ডের বর্তমান মালিক বা মালিকদের নামের সাথে মেলে না। | needs native review |
| `rules.R-OWN-01.next` | বিক্রেতার কাছে খতিয়ান, জাতীয় পরিচয়পত্র এবং কীভাবে জমির মালিক হয়েছেন তার প্রমাণ চান। | needs native review |
| `rules.R-OWN-02.title` | বিক্রেতার নাম আংশিক মিলেছে | needs native review |
| `rules.R-OWN-02.explain` | নামটি রেকর্ডের সাথে কেবল {{tier}} মাত্রায় মিলেছে। এটি বানানের পার্থক্য হতে পারে, আবার অন্য মানুষও হতে পারে। | needs native review |
| `rules.R-OWN-02.next` | জাতীয় পরিচয়পত্র, পিতার নাম ও দলিল রেকর্ডের সাথে মিলিয়ে দেখুন। | needs native review |
| `rules.R-DISP-01.title` | এই জমি নিয়ে একটি মামলা আছে | needs native review |
| `rules.R-DISP-01.explain` | {{court}}-এর মামলা {{case_ref}} এই জমির সাথে যুক্ত ({{linkage}})। | needs native review |
| `rules.R-DISP-01.next` | কোনো টাকা দেওয়ার আগে আইনজীবীকে দিয়ে মামলার নথি পড়িয়ে নিন। | needs native review |
| `rules.R-DISP-02.title` | একটি মামলা এই জমির সাথে সম্পর্কিত হতে পারে | needs native review |
| `rules.R-DISP-02.explain` | মামলা {{case_ref}}-এ বিক্রেতার মতো নাম আছে, কিন্তু এই দাগ নম্বরের সাথে সরাসরি যুক্ত নয়। | needs native review |
| `rules.R-DISP-02.next` | মামলাটি এই জমির সাথে সম্পর্কিত কি না আইনজীবীকে দিয়ে নিশ্চিত করুন। | needs native review |
| `rules.R-DISP-03.title` | একটি নামজারি অপেক্ষমাণ | needs native review |
| `rules.R-DISP-03.explain` | নামজারির আবেদন {{mutation_ref}} এখনো অপেক্ষমাণ। {{applicant_note}} | needs native review |
| `rules.R-DISP-03.next` | টাকা দেওয়ার আগে ভূমি অফিসে জিজ্ঞেস করুন কে আবেদন করেছেন এবং কেন। | needs native review |
| `rules.R-RES-01.title` | জমিটি সরকারি খাস তালিকায় আছে | needs native review |
| `rules.R-RES-01.explain` | রেকর্ড {{record_ref}}-এ এই জমি সরকারি খাস জমি হিসেবে তালিকাভুক্ত। | needs native review |
| `rules.R-RES-01.next` | টাকা দেবেন না। সহকারী কমিশনার (ভূমি) অফিসে জিজ্ঞেস করুন। | needs native review |
| `rules.R-RES-02.title` | জমিটি {{list}} তালিকায় আছে | needs native review |
| `rules.R-RES-02.explain` | রেকর্ড {{record_ref}} এই জমিকে সরকারি নিয়ন্ত্রণাধীন জমির {{list}} তালিকায় রেখেছে। | needs native review |
| `rules.R-RES-02.next` | টাকা দেবেন না। সহকারী কমিশনার (ভূমি) অফিসে জিজ্ঞেস করুন। | needs native review |
| `rules.R-LIEN-01.title` | ব্যাংক বন্ধক আছে | needs native review |
| `rules.R-LIEN-01.explain` | {{bank_name}}-এর নিবন্ধিত বন্ধক ({{lien_ref}}) এই জমিতে আছে। | needs native review |
| `rules.R-LIEN-01.next` | টাকা দেওয়ার আগে ব্যাংকের মুক্তিপত্র চান। | needs native review |
| `rules.R-SALE-01.title` | দুটি বিক্রয় দলিল একে অপরের সাথে মিলে যাচ্ছে | needs native review |
| `rules.R-SALE-01.explain` | দলিল {{deed_a}} ও {{deed_b}} দুটোই একই জমির অংশ বিক্রি করেছে ({{overlap}})। | needs native review |
| `rules.R-SALE-01.next` | কোন দলিল বৈধ তা আইনজীবী না বোঝানো পর্যন্ত টাকা দেবেন না। | needs native review |
| `rules.R-CHAIN-03.title` | জরিপের মধ্যে জমির পরিমাণ বদলেছে | needs native review |
| `rules.R-CHAIN-03.explain` | {{from_survey}}-এ পরিমাণ ছিল {{from_area}} শতক, {{to_survey}}-এ হয়েছে {{to_area}} শতক ({{drift_pct}}% পরিবর্তন)। | needs native review |
| `rules.R-CHAIN-03.next` | সার্ভেয়ারের মাপ এবং পরিবর্তনের কারণ চান। | needs native review |
| `rules.R-CHAIN-04.title` | জমির শ্রেণি বদলেছে | needs native review |
| `rules.R-CHAIN-04.explain` | জমির শ্রেণি {{from_class}} থেকে {{to_class}} হয়েছে। | needs native review |
| `rules.R-CHAIN-04.next` | কোন অনুমোদনে এই পরিবর্তন হয়েছে তা জিজ্ঞেস করুন। | needs native review |
| `rules.R-INT-01.title` | রেকর্ডের ইতিহাস অখণ্ডতা পরীক্ষায় ব্যর্থ | needs native review |
| `rules.R-INT-01.explain` | বদল-ধরা লগ {{broken_at_seq}} নম্বর এন্ট্রিতে ভেঙে গেছে: {{reason}}। | needs native review |
| `rules.R-INT-01.next` | এই ফলাফলের ওপর ভরসা করবেন না। ভূমি অফিসকে জানান এবং নতুন সত্যায়িত কপি চান। | needs native review |
| `rules.R-INT-02.title` | {{source}}-এর তথ্য পুরোনো | needs native review |
| `rules.R-INT-02.explain` | {{source}}-এর সর্বশেষ তথ্য {{as_of}} তারিখের। | needs native review |
| `rules.R-INT-02.next` | ওই অফিস থেকে হালনাগাদ সত্যায়িত কপি চান। | needs native review |
| `rules.R-INT-03.title` | {{source}} যাচাই করা যায়নি | needs native review |
| `rules.R-INT-03.explain` | {{source}} উত্তর দেয়নি ({{reason}})। | needs native review |
| `rules.R-INT-03.next` | পরে আবার চেষ্টা করুন এবং ওই অফিস থেকে সত্যায়িত কপি চান। | needs native review |
| `rules.R-INFO-01.title` | বিক্রেতার নাম রেকর্ডের সাথে মিলেছে | needs native review |
| `rules.R-INFO-01.explain` | বিক্রেতার নাম বর্তমান রেকর্ডের সাথে জোরালোভাবে মিলেছে। | needs native review |
| `rules.R-INFO-01.next` | তবুও বিক্রেতার জাতীয় পরিচয়পত্র ও পিতার নাম যাচাই করুন। | needs native review |
| `rules.R-INFO-02.title` | মালিকানার ইতিহাস পাওয়া গেছে | needs native review |
| `rules.R-INFO-02.explain` | আমরা {{depth}} প্রজন্মের মালিকানা অনুসরণ করেছি। | needs native review |
| `rules.R-INFO-02.next` | তবুও আইনজীবীকে দিয়ে দলিলগুলো পড়িয়ে নিন। | needs native review |
| `rules.R-INFO-03.title` | সর্বশেষ হস্তান্তরের তারিখ | needs native review |
| `rules.R-INFO-03.explain` | সর্বশেষ নথিভুক্ত হস্তান্তর হয়েছে {{last_transfer_date}} তারিখে। | needs native review |
| `rules.R-INFO-03.next` | ওই দলিলটি দেখতে চান এবং তাতে উল্লিখিত মানুষদের পরিচয় মিলিয়ে নিন। | needs native review |
| `rules.R-OWN-03.title` | বিক্রেতার অংশ বিক্রির পরিমাণের চেয়ে কম | needs native review |
| `rules.R-OWN-03.explain` | বিক্রেতার অংশ {{seller_share}}, কিন্তু তিনি {{selling_share}} বিক্রি করছেন। | needs native review |
| `rules.R-OWN-03.next` | প্রত্যেক সহ-মালিককে দলিলে সই করতে বলুন। | needs native review |
| `rules.R-CHAIN-01.title` | মালিকানার ধারায় একটি যোগসূত্র নেই | needs native review |
| `rules.R-CHAIN-01.explain` | এক মালিকের কাছ থেকে পরের মালিকের কাছে জমি কীভাবে গেল তা রেকর্ডে দেখা যায় না। | needs native review |
| `rules.R-CHAIN-01.next` | যে দলিল বা উত্তরাধিকার নথি এই ফাঁক পূরণ করে তা চান। | needs native review |
| `rules.R-CHAIN-02.title` | রেকর্ডে অংশের যোগফল মেলে না | needs native review |
| `rules.R-CHAIN-02.explain` | রেকর্ডে অংশের যোগফল {{share_sum}}, ১ নয়। | needs native review |
| `rules.R-CHAIN-02.next` | আইনজীবীকে দিয়ে অংশগুলো মিলিয়ে নিন। | needs native review |
| `rules.R-RES-03.title` | পুরোনো রেকর্ডে জমিটি সরকারি হওয়ার ইঙ্গিত আছে | needs native review |
| `rules.R-RES-03.explain` | রেকর্ড {{record_ref}} ইঙ্গিত দেয় জমিটি একসময় সরকারি জমি ছিল। | needs native review |
| `rules.R-RES-03.next` | টাকা দেওয়ার আগে সহকারী কমিশনার (ভূমি) অফিসে জিজ্ঞেস করুন। | needs native review |
| `rules.R-INT-04.title` | দুটি উৎসের তথ্য মেলে না | needs native review |
| `rules.R-INT-04.explain` | {{source_a}} ও {{source_b}} এই জমি নিয়ে পরস্পরবিরোধী তথ্য দিচ্ছে। | needs native review |
| `rules.R-INT-04.next` | দুই অফিস থেকেই সত্যায়িত কপি চান। | needs native review |
| `rules.fallback.title` | পর্যবেক্ষণ {{rule_id}} | needs native review |
| `rules.fallback.explain` | এই অ্যাপের বর্তমান সংস্করণে এই পর্যবেক্ষণের বর্ণনা নেই। | needs native review |
| `rules.fallback.next` | আইনজীবীকে দিয়ে এই প্রতিবেদন দেখিয়ে নিন। | needs native review |
| `rules.applicantSeller` | আবেদনকারী বিক্রেতা নিজেই। | needs native review |
| `rules.applicantOther` | আবেদনকারী বিক্রেতা নন, অন্য কেউ। | needs native review |
| `rules.evidence` | প্রমাণসূত্র | needs native review |
| `rules.nextStep` | পরবর্তী ধাপ | needs native review |
| `notChecked.source_unavailable` | {{source}} যাচাই করা যায়নি ({{reason}})। | needs native review |
| `notChecked.source_stale` | {{source}}-এর তথ্য {{as_of}} তারিখের, তাই পুরোনো হতে পারে। | needs native review |
| `notChecked.source_partial` | {{source}} আংশিক উত্তর দিয়েছে। | needs native review |
| `notChecked.linkage_party_name_only` | {{source}} শুধু নাম ধরে খোঁজা হয়েছে, তাই রেকর্ড না পাওয়া মানে রেকর্ড নেই এমন নয়। | needs native review |
| `notChecked.low_maturity` | {{source}} আংশিক ডিজিটাল (তথ্যের স্তর {{maturity}})। | needs native review |
| `notChecked.static_physical_possession` | জমি আসলে কার দখলে আছে। | needs native review |
| `notChecked.static_boundaries` | মাঠে জমির সীমানা আসলে কোথায়। | needs native review |
| `notChecked.static_unregistered_agreements` | অনিবন্ধিত চুক্তি বা দাবি। | needs native review |
| `notChecked.static_equitable_mortgage` | মূল দলিল জমা রেখে করা অনানুষ্ঠানিক বন্ধক। | needs native review |
| `notChecked.static_seller_documents` | বিক্রেতার পরিচয়পত্র ও তাঁর হাতে থাকা দলিল। | needs native review |
| `notChecked.static_legal_review` | আইনজীবীর করা দলিল পর্যালোচনা। | needs native review |
| `notChecked.fallback` | আরও একটি বিষয় যা আমরা যাচাই করতে পারিনি। | needs native review |
