# 2021-03-26 05:46:39.187128
python train_wae.py --experiment_name=64x64/experiments_v1/inp_noise --convar_type=naive --inpainter_type=noise --batch_size 48 --dataset celeba --img_size 64 --mask_hidden_h 32 --mask_hidden_w 32 --num_epochs=10 --render_every 2 --lr=4e-4 --wae_fc=16 --wae_lc=16 --wae_depth=3 --wae_bl=2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --max_benchmark_batches=-1
