# 2021-05-03 23:53:17.639665
python train_wae.py --experiment_name=64x64/experiments_v5_long_training/inp_acflow --inpainter_type=acflow --inpainter_path ../../ACFlow/exp/celeba/rnvp/ --batch_size 16 --dataset celeba --img_size 64 --mask_train_size 32 --mask_val_size 32 --num_epochs=50 --render_every 2 --lr=1e-4 --wae_fc=64 --wae_lc=64 --wae_depth=4 --wae_bl=4 --wae_latent_size=64 --wae_disc_hidden 512 --wae_recon_loss mse --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --max_benchmark_batches -1 --wae_disc_loss_weight 0.025
