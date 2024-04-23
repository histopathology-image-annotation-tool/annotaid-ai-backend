# CHANGELOG



## v0.7.0 (2024-04-23)

### Feature

* feat: update MC models to v2 ([`8d0f905`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/8d0f905b89fbd64827e2d9536ab1702b90657663))

### Unknown

* Merge branch &#39;feat/mc_model&#39; ([`6b90af9`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/6b90af94192250076b0f3d8a0299ca0b9100a187))


## v0.6.0 (2024-04-20)

### Chore

* chore: update poetry version ([`75ae625`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/75ae62511d13d41ab9c7855fc1ff3d3e6b46198b))

* chore: update pre-commit hooks ([`9c078a9`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/9c078a9f74b1674c132306343f2bdf7fa8db1ba7))

* chore: update dev dependencies ([`138657a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/138657a6f636568c3e97b38388baabf04533cc2a))

* chore: fix nvidia dependencies [skip ci] ([`dfc23dd`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/dfc23ddb1048ed97dc2550b828329818132ea444))

### Documentation

* docs: add comments for the AL celery tasks and API ([`ebc20f6`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ebc20f6c9561e78d2d4aba9a734ae46a4593285e))

### Feature

* feat: add a check if celery tasks exist for result retrieving API endpoints ([`1f3c613`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/1f3c613fe8fb258e49acad1ffec92a0586ff9adb))

* feat: add model hash column for the predictions table ([`3258e1a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/3258e1ae7496c9dc532fa68ec65f5a50d4989cd4))

* feat: add possibility to filter only slides with predictions ([`81c5257`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/81c5257fb9842e709bf0ef98750b54667235f875))

* feat: add full-text search for slide path ([`0070352`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0070352a0343408f69265f3b2215aeabf13fc1c3))

### Fix

* fix: prepopulate result key only for my tasks ([`1ce6736`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/1ce67361f45e056efb83f1ee1abbb31c52cf133d))

* fix: AL task routing ([`38590ba`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/38590ba83022eddb1aabeb040520c8f6155cb62c))

* fix: semantic release version variable in pyproject ([`cf87207`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/cf872072839edc97bd7fff1399caa175e89d6860))

### Unknown

* Merge branch &#39;feat/AL_slides&#39; ([`86dbf93`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/86dbf93524b165d0f1c24e1dafe72193905474de))


## v0.5.0 (2024-04-09)

### Chore

* chore: fix nvidia dependencies [skip ci] ([`7827e19`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7827e19545db7334214671d7d15f6d7930e5b698))

* chore: fix nvidia dependencies [skip ci] ([`f24eb6d`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f24eb6dbef96e59149a22434b7d9d4f10936a335))

### Feature

* feat: add checksum check for downloading model weights ([`db9670e`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/db9670e4e485cc4da1c84a2711c6ca3a82a83976))

* feat: add prediction_id to Annotation response and fix saving annotation message ([`d3f018f`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/d3f018fb2f4e6714ad5eef113f6947209bd7f6ad))

### Fix

* fix: download weight script paths ([`427e86b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/427e86bb513e3b48f7b1ee5fdb48468997962762))

* fix: MC celery task ([`6661f20`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/6661f202364f4f340f40a884d588bdfa24f5ab80))

### Unknown

* Merge branch &#39;fix/AL&#39; ([`6372a27`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/6372a271b1320977b45ad824f4b7b51d88721691))


## v0.4.0 (2024-04-07)

### Chore

* chore: update dependencies [skip ci] ([`87446bc`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/87446bcfcd279029d673eeeb037b5ee21af498ef))

### Feature

* feat: add user_annotated and total counts for AL endpoints ([`22aa20f`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/22aa20f8fff805044bb81dff86421769f43fc707))

### Fix

* fix: docker entrypoint for backend ([`0dd2688`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0dd2688469762b65e73c117bab0e52f25f2f624f))

* fix: AL redis memory OOM ([`7649523`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/76495239386c7f0e814f361060388fb65c7d9c76))

### Unknown

* Merge branch &#39;feat/prediction_counts&#39; ([`8b22065`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/8b22065f8cb8afb932115e90ae7842ca99e44c8b))


## v0.3.0 (2024-04-05)

### Chore

* chore: fix nvidia dependencies ([`bf27435`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/bf2743509e85646098c511f7bf8fbffcf5248b59))

* chore(release): v0.2.4 [skip ci] ([`e8cd9c9`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/e8cd9c90b4211ea47d67f024f3662d46267fc2d9))

* chore(release): v0.2.3 [skip ci] ([`a66c082`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/a66c0827d460b7eaeb5f863f3a21915bfd29a7c8))

* chore(release): v0.2.2 [skip ci] ([`654cff3`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/654cff370e7348d84cd4af41af35f116030888b5))

* chore(release): v0.2.1 [skip ci] ([`be117b9`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/be117b95db71b53864262b6f0daa91db1a4978a0))

* chore(release): v0.2.0 [skip ci] ([`0a61712`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0a61712c53ba42fdb2eb9292f32960f56cc94254))

* chore: update LICENSE and README [skip ci] ([`0fe196b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0fe196b115c1af0e0831e308dfe4f1f33133dd7c))

### Ci

* ci: stop building docker images when no release is done ([`9888973`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/98889739f0671f35a7b70fce2737e35aed50ff08))

* ci: stop building docker images when no release is done ([`51b1665`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/51b166574a68bc7f8f1116a3f7d9e764db2887e3))

* ci: stop building docker images when no release is done ([`ae82929`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ae829290ad52dba6c48ebcfce0a8719f62e1e8f6))

* ci: stop building docker images when no release is done ([`ce5062b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ce5062b478cc0050faa46a09555204b4b6167a27))

### Feature

* feat: update migrations and add watchdog ([`2e0421a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/2e0421a045d484d8247e90de60ba6b3fcb34dc40))

* feat: add alembic migrations ([`a256543`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/a256543905e8b7738605f7ae1d7b4b0cdf8f8a27))

* feat: add AL queue to celery ([`59af91d`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/59af91de03e7e7d1ae18231a9b189d42a84e7191))

* feat: update Dockerfiles, Makefile and README ([`d9073f2`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/d9073f25381133f89aa78fa8fcba54ac6268bfbd))

* feat: add get_slide_annotations endpoint and update existing ([`58cf2f5`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/58cf2f59a1e5660b18832e3a6211bae5758b0318))

* feat: add active learning endpoints ([`fb56992`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/fb56992508c84399722d22beb1daa7e345c815f5))

* feat: add active learning celery jobs ([`7b16333`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7b1633363b68281c79d4a20717eddbd6c9900df6))

* feat: update .env.example ([`9064967`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/90649673c6fa1ed1e73a7ffc580f59a0bebd32f1))

* feat: add middleware for pagination ([`bf8b3fd`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/bf8b3fd4410661939bb8cfb418494a71cacc1a93))

* feat: add schemas for active learning ([`666c133`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/666c1332ed72424c7786f5145df32a06e3b9dfa6))

* feat: setup database connection ([`fb1a376`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/fb1a37612614231c53b42f801fbc6d285b1461f2))

* feat: add active learning database models ([`5d6dc87`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/5d6dc873f2dc7aa95dfcdb3c9e38bd18ecb60496))

### Fix

* fix: mc endpoint ([`11f13d8`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/11f13d8e3da8e8dffc2c6566eb5c05c8d81f218e))

* fix: add missing dependency ([`872a82f`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/872a82f361f1d71bb7eacd99e92e37b7d1a96b8d))

* fix: dependencies ([`0f48a0c`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0f48a0c2825f02ec0445213fba67925b75e800f3))

* fix: shapely dependency ([`34dd5fa`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/34dd5fad5170e545ce79183448f23cddaa8a63dc))

* fix: update dependecies ([`9d43b3b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/9d43b3b60c4059ac1110fa31160e15fd25dc7ca2))

* fix: psycopg2 package ([`edf9c73`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/edf9c7344d115ac69ec443e149f8362c2f56d104))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend ([`a78948b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/a78948b3a38475ab594cf866b028638c14243ea8))

* Merge branch &#39;fix/active_learning&#39; ([`7ddce53`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7ddce53871546b6affa758ff62fa95cbc4168608))

* Merge branch &#39;main&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend ([`43959a8`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/43959a8ae66f752c913d07c5bd1fc2913dcb4710))

* Merge branch &#39;feat/active_learning&#39; ([`74d0b23`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/74d0b23540f29268d72f327a899af05e16b3eb32))

* Merge branch &#39;main&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend ([`1a0c242`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/1a0c2428d80f232a674728da0e882a3b25091697))


## v0.1.0 (2024-03-10)

### Chore

* chore(release): v0.1.0 [skip ci] ([`10faa9d`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/10faa9d9506be064457e4110588dbd96cff22a58))

* chore(release): v0.1.0 [skip ci] ([`e2f9450`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/e2f9450bfc6e4159a845a869beabff55834c8eaa))

* chore(release): v0.1.0 [skip ci] ([`3c011ed`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/3c011ed28b8d227ba99a190032dea27e8e4ff922))

* chore(release): v0.1.0 [skip ci] ([`0c282e8`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0c282e8f959808de3a8f32c17d7d4cace8549afb))

* chore(release): v0.1.0 [skip ci] ([`e13feed`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/e13feed286898d8e2d580511d10b4055039ee60d))

* chore(release): v0.2.0 [skip ci] ([`4f91070`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/4f91070162f565a34510519aa0e05ed108cc28f1))

* chore(release): v0.1.0 [skip ci] ([`886891e`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/886891ebed26007e69be2b15479248c6e3beb8f2))

* chore(release): v0.1.0 [skip ci] ([`e5cf514`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/e5cf5145446bb432286154a51b7b36b01f4d2fa3))

* chore(release): v0.1.0 [skip ci] ([`5953ff0`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/5953ff029f9450b97b6b1abee7544a7ba91a2ab5))

* chore(release): v0.1.0 [skip ci] ([`63cc334`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/63cc3342dd6d124e7d3da0720bcf420ec79efa14))

* chore(release): v0.1.0 [skip ci] ([`da39c8a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/da39c8a2635a56d31d961d17c5a0b6025390d982))

* chore(release): 1.0.0 [skip ci]

# 1.0.0 (2024-03-04)

### Bug Fixes

* cors ([b9d5129](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/b9d5129cae3126592dea0b0851c898fe630a5a44))
* cors ([03f4fd7](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/03f4fd7dbfeee0c4750ac20b2a5a02d529ec3ad0))
* dockerhub.yaml ([4671fbd](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/4671fbd09a675667dbb8c801162dbd1757ebc4d7))
* download weights ([394dfc2](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/394dfc2b937580b4243fddefe97787e41df24322))
* Makefile and tags ([7e176a0](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7e176a0cafaa61fce9a3e9b12f375049eee22e54))
* NormalizeHEStains error ([0415a25](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0415a25df8b9b3fec38906d5ebd2e022b327ed55))
* return previous_predict_task_id in SAMPredictResponse ([f439fb4](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f439fb4e8889e9f218510dc2a59970dc6531b760))

### Features

* add api for nuclick and mitosis detection ([412533a](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/412533ae64d6c422939f8fa7e4ed03581ee75559))
* add config files ([edeb5ee](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/edeb5ee69210290ba398da8425b7a6c6668cb27e))
* add dockerfiles ([2700b37](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/2700b37acc3dfb561322eecc98da09860c13977e))
* add nuclear pleomorphism ([ffb1bf2](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ffb1bf2d1116245c74a2347b6a10242d88b3a5f3))
* add nuclick bbox dense prediction and update API routes ([f171199](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f1711995b7629224a66240e0d22b3d5821772ffc))
* add SAHI prediction for MC first-stage model ([62a8e83](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/62a8e8341523af42ba5a3523cb2f580e31c8958b))
* add SAM model ([ce640ac](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ce640aca7534b0f0ef380892b607a97974006538))
* add SAM postprocessing config ([a9abd32](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/a9abd324dbd71d25a200c2d70817325e3a2c749e))
* update docker python version ([8f793bc](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/8f793bc3f17df3144f7e41d65386c0985d82ab04)) ([`290e617`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/290e61757cd9b07ef138750de049cc12a4142532))

* chore: update README.md ([`dcf28a1`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/dcf28a1a65c6230f37cf018e9be488f1a42ec3d1))

* chore: update LICENSE ([`214956f`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/214956fea5bf1b2b208946e797e925277cf1bfae))

* chore: update LICENSE ([`4a66b30`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/4a66b304d4d102d59bced3eaf8abd0883535b444))

### Ci

* ci: update dependencies ([`80fa943`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/80fa943dd4d61944bffa045b71023e8d39bc659e))

* ci: update branch in release workflow ([`07f207a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/07f207aeeb1aedfaece3093d8d8b66f4fec396e4))

* ci: fix dockerfile paths ([`5c87cdf`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/5c87cdf4d76c559f93fc4742ab830e2c1b56e0c6))

* ci: parallel backend and worker docker image build ([`f11e7b4`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f11e7b41b8bffff9422afbeb4447f5c627306ecb))

* ci: fix build pipeline ([`db991ca`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/db991ca758c54388140dce21795d4664d753bda5))

* ci: update docker workflow tags ([`0d762e9`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0d762e93a38abd1913f38ee57d4c82c1483fed89))

* ci: update docker workflow tags ([`55e4570`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/55e4570222eb8d410495878088a502b87e211a03))

* ci: add docker build with released tag ([`bd0fb66`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/bd0fb668979712f7c69c6ebe9a213148221fce1e))

* ci: fetch depth in release ([`7fdbb85`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7fdbb85ffe1ae139a10d2d4cff6868f8b610485a))

* ci: semantic release ([`e2ceb54`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/e2ceb54f9b77808715e54bc7b6ce686196a5dcea))

* ci: add deploy to dockerhub ([`84a7091`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/84a7091c505828b7248937a1da987dfa7165f5cd))

### Documentation

* docs: add docstrings ([`d82c2ee`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/d82c2ee215d7f8fd4af03261773cf06ff741c663))

### Feature

* feat: add semantic release ([`5b9a4ca`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/5b9a4ca5efbe6cac31c7c60c9e5f58df498615c9))

* feat: update docker python version ([`8f793bc`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/8f793bc3f17df3144f7e41d65386c0985d82ab04))

* feat: add SAM postprocessing config ([`a9abd32`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/a9abd324dbd71d25a200c2d70817325e3a2c749e))

* feat: add SAHI prediction for MC first-stage model ([`62a8e83`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/62a8e8341523af42ba5a3523cb2f580e31c8958b))

* feat: add SAM model ([`ce640ac`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ce640aca7534b0f0ef380892b607a97974006538))

* feat: add nuclick bbox dense prediction and update API routes ([`f171199`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f1711995b7629224a66240e0d22b3d5821772ffc))

* feat: add nuclear pleomorphism ([`ffb1bf2`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/ffb1bf2d1116245c74a2347b6a10242d88b3a5f3))

* feat: add dockerfiles ([`2700b37`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/2700b37acc3dfb561322eecc98da09860c13977e))

* feat: add config files ([`edeb5ee`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/edeb5ee69210290ba398da8425b7a6c6668cb27e))

* feat: add api for nuclick and mitosis detection ([`412533a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/412533ae64d6c422939f8fa7e4ed03581ee75559))

### Fix

* fix: update version dependencies ([`08c751c`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/08c751c6ccfd1e42ff36e84218d3a3606f998d71))

* fix: update version dependencies ([`c2c192f`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/c2c192fa91a316df98d7bb95a8bb304693bdce1c))

* fix: remove CHANGELOG ([`b33424a`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/b33424aa59bb9efaadda2bf324f516190f2839ee))

* fix: remove CHANGELOG ([`eb08f3c`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/eb08f3c37e45c129888ed2a8176bc857a3ee466a))

* fix: remove CHANGELOG ([`56d3c74`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/56d3c74262f5a69638a99ad8db14413fbd579f79))

* fix: download weights ([`394dfc2`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/394dfc2b937580b4243fddefe97787e41df24322))

* fix: return previous_predict_task_id in SAMPredictResponse ([`f439fb4`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/f439fb4e8889e9f218510dc2a59970dc6531b760))

* fix: NormalizeHEStains error ([`0415a25`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/0415a25df8b9b3fec38906d5ebd2e022b327ed55))

* fix: cors ([`b9d5129`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/b9d5129cae3126592dea0b0851c898fe630a5a44))

* fix: cors ([`03f4fd7`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/03f4fd7dbfeee0c4750ac20b2a5a02d529ec3ad0))

* fix: Makefile and tags ([`7e176a0`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7e176a0cafaa61fce9a3e9b12f375049eee22e54))

* fix: dockerhub.yaml ([`4671fbd`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/4671fbd09a675667dbb8c801162dbd1757ebc4d7))

### Unknown

* Merge branch &#39;feat/semantic_release&#39; ([`1d8a431`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/1d8a431ec8a112aff174953c2b142b715d272e22))

* Merge branch &#39;main&#39; into feat/semantic_release ([`8abcbd8`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/8abcbd8a65ea6904e9519cf97c5c8f76251a4671))

* Merge branch &#39;feat/semantic_release&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend into feat/semantic_release ([`5784eba`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/5784ebac6f9fe435252b86cee393dd0b5cdd447f))

* Merge branch &#39;feat/semantic_release&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend into feat/semantic_release ([`7395239`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7395239076978248e998a4e250f5e583827cdfdc))

* Merge branch &#39;feat/semantic_release&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend into feat/semantic_release ([`c629e4b`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/c629e4bf452ef56784dcdcede7c95a1c9ca02c58))

* Merge branch &#39;feat/semantic_release&#39; of https://github.com/histopathology-image-annotation-tool/annotaid_ai_backend into feat/semantic_release ([`1b82b86`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/1b82b86926d0d33fa299edee90bffba9de846025))

* Initial commit ([`7a4a0eb`](https://github.com/histopathology-image-annotation-tool/annotaid-ai-backend/commit/7a4a0eb3f3578c227e6540ecdc103d06ff733dda))
