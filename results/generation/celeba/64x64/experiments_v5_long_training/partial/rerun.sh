# 2021-05-09 00:11:17.002276
python train_wae.py --experiment_name=64x64/experiments_v5_long_training/partial --convar_type=partial --inpainter_type=zero --batch_size 24 --dataset celeba --img_size 64 --mask_train_size 32 --mask_val_size 32 --num_epochs=50 --render_every 2 --lr=1e-4 --wae_fc=64 --wae_lc=64 --wae_depth=4 --wae_bl=4 --wae_latent_size=64 --wae_disc_hidden 512 --wae_recon_loss mse --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --max_benchmark_batches -1 --wae_disc_loss_weight 0.025
